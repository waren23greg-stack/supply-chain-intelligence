from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from backend.webhooks import router as webhooks_router
from backend.db import get_db
from data_pipeline.models import ERPInventoryTable, SupplierTable
from intelligence_engine.schemas import SupplyChainState, SKUInventory, SupplierData
from intelligence_engine.agents import run_supply_chain_pipeline
from intelligence_engine.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multi-Agent Supply Chain Intelligence Engine API (PostgreSQL Powered)"
)

app.include_router(webhooks_router)

# Enable CORS for front-end decision dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _convert_db_to_state(sku_record: ERPInventoryTable) -> SupplyChainState:
    """
    Helper function that translates SQLAlchemy ORM models into clean Pydantic state schemas
    for our multi-agent AI pipeline.
    """
    if not sku_record.primary_supplier:
        raise HTTPException(
            status_code=404, 
            detail=f"Supplier code '{sku_record.primary_supplier_code}' not found for SKU '{sku_record.sku}'"
        )
    
    sku_model = SKUInventory(
        sku=sku_record.sku,
        name=sku_record.name,
        current_stock=sku_record.current_stock,
        daily_burn_rate=sku_record.daily_burn_rate,
        primary_supplier_id=sku_record.primary_supplier_code,
        in_transit_qty=sku_record.in_transit_qty
    )
    
    supplier_model = SupplierData(
        supplier_id=sku_record.primary_supplier.supplier_code,
        name=sku_record.primary_supplier.name,
        country=sku_record.primary_supplier.country,
        historical_otif_rate=sku_record.primary_supplier.historical_otif_rate,
        lead_time_days=sku_record.primary_supplier.lead_time_days,
        geopolitical_risk_index=sku_record.primary_supplier.geopolitical_risk_index
    )
    
    return SupplyChainState(sku_data=sku_model, supplier_data=supplier_model)

@app.get("/health")
def health_check():
    return {"status": "operational", "engine": settings.APP_NAME, "database": "PostgreSQL"}

@app.get("/api/v1/sku-risk/{sku}", response_model=SupplyChainState)
def get_sku_risk_from_db(sku: str, db: Session = Depends(get_db)):
    """
    Queries an SKU from PostgreSQL, fetches its supplier data, and runs AI risk analysis.
    """
    stmt = select(ERPInventoryTable).where(ERPInventoryTable.sku == sku.upper())
    sku_record = db.execute(stmt).scalar_one_or_none()
    
    if not sku_record:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' not found in database.")
    
    initial_state = _convert_db_to_state(sku_record)
    return run_supply_chain_pipeline(initial_state)

@app.get("/api/v1/all-risks", response_model=List[SupplyChainState])
def analyze_all_inventory_risks(db: Session = Depends(get_db)):
    """
    Scans every SKU in the PostgreSQL database through the multi-agent pipeline
    to generate an enterprise-wide risk scorecard.
    """
    stmt = select(ERPInventoryTable)
    all_skus = db.execute(stmt).scalars().all()
    
    if not all_skus:
        raise HTTPException(status_code=404, detail="No inventory records found. Run database seeding first.")
    
    results = []
    for sku_record in all_skus:
        state = _convert_db_to_state(sku_record)
        evaluated_state = run_supply_chain_pipeline(state)
        results.append(evaluated_state)
        
    return results

@app.post("/api/v1/analyze-sku-risk", response_model=SupplyChainState)
def analyze_sku_risk_manual(payload: SupplyChainState):
    """
    Runs a user-supplied JSON payload through the multi-agent pipeline for What-If testing.
    """
    try:
        return run_supply_chain_pipeline(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence pipeline error: {str(e)}")
