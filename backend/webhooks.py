import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from backend.db import get_db
from data_pipeline.models import SupplierTable, ERPInventoryTable
from intelligence_engine.schemas import (
    SupplierDisruptionWebhook, 
    WebhookResponse, 
    SupplyChainState, 
    SKUInventory, 
    SupplierData, 
    RiskLevel
)
from intelligence_engine.agents import run_supply_chain_pipeline

logger = logging.getLogger("SupplyChainWebhooks")
router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks & External Alerts"])

@router.post("/supplier-alert", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
def process_supplier_disruption_webhook(
    payload: SupplierDisruptionWebhook, 
    db: Session = Depends(get_db)
):
    """
    Ingests real-time supply chain disruption alerts, updates supplier risk metrics in PostgreSQL,
    and recalculates inventory stockout probabilities for all affected SKUs.
    """
    logger.info(f"Received webhook alert for {payload.supplier_code}: {payload.disruption_type}")

    # 1. Look up Supplier in Database
    stmt = select(SupplierTable).where(SupplierTable.supplier_code == payload.supplier_code.upper())
    supplier = db.execute(stmt).scalar_one_or_none()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier code '{payload.supplier_code}' not found in database."
        )

    # 2. Dynamically adjust supplier risk metrics based on webhook severity
    supplier.geopolitical_risk_index = min(1.0, max(0.0, payload.severity))
    
    # If the alert reports explicit delays, degrade historical OTIF slightly
    if payload.estimated_delay_days > 5:
        supplier.historical_otif_rate = max(0.40, supplier.historical_otif_rate - 0.15)
    
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    # 3. Fetch all SKUs tied to this supplier
    sku_stmt = select(ERPInventoryTable).where(
        ERPInventoryTable.primary_supplier_code == supplier.supplier_code
    )
    affected_skus = db.execute(sku_stmt).scalars().all()

    new_critical_alerts = []

    # 4. Re-run multi-agent pipeline for every SKU impacted by this supplier
    supplier_model = SupplierData(
        supplier_id=supplier.supplier_code,
        name=supplier.name,
        country=supplier.country,
        historical_otif_rate=supplier.historical_otif_rate,
        lead_time_days=supplier.lead_time_days,
        geopolitical_risk_index=supplier.geopolitical_risk_index
    )

    for sku_record in affected_skus:
        sku_model = SKUInventory(
            sku=sku_record.sku,
            name=sku_record.name,
            current_stock=sku_record.current_stock,
            daily_burn_rate=sku_record.daily_burn_rate,
            primary_supplier_id=sku_record.primary_supplier_code,
            in_transit_qty=sku_record.in_transit_qty
        )

        state = SupplyChainState(sku_data=sku_model, supplier_data=supplier_model)
        evaluated_state = run_supply_chain_pipeline(state)

        # Collect any SKUs escalated to CRITICAL or HIGH risk
        if evaluated_state.risk_alert and evaluated_state.risk_alert.risk_level in [
            RiskLevel.CRITICAL, RiskLevel.HIGH
        ]:
            new_critical_alerts.append(evaluated_state.risk_alert)

    logger.info(
        f"Recalculation complete. {len(new_critical_alerts)} critical alerts triggered for {supplier.name}."
    )

    return WebhookResponse(
        status="ALERT_PROCESSED",
        supplier_code=supplier.supplier_code,
        supplier_name=supplier.name,
        updated_risk_index=supplier.geopolitical_risk_index,
        affected_skus_count=len(affected_skus),
        new_critical_alerts=new_critical_alerts
    )
