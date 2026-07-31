import pytest
from intelligence_engine.schemas import (
    SupplyChainState, SKUInventory, SupplierData, RiskLevel
)
from intelligence_engine.agents import run_supply_chain_pipeline
from intelligence_engine.simulations import MonteCarloSimulator

def test_critical_stockout_detection():
    """
    Verifies that an SKU with low stock and a high-risk supplier triggers a CRITICAL alert.
    """
    sku = SKUInventory(
        sku="TEST-SKU-001",
        name="Critical Component",
        current_stock=100,      # Only 10 days of stock at burn rate 10
        daily_burn_rate=10,
        primary_supplier_id="SUP-TEST-01",
        in_transit_qty=0
    )
    supplier = SupplierData(
        supplier_id="SUP-TEST-01",
        name="High Risk Supplier",
        country="Country X",
        historical_otif_rate=0.60,  # Low OTIF triggers delay penalties
        lead_time_days=20,          # Base lead time already exceeds stock
        geopolitical_risk_index=0.80
    )
    
    state = SupplyChainState(sku_data=sku, supplier_data=supplier)
    result = run_supply_chain_pipeline(state)
    
    assert result.risk_alert is not None
    assert result.risk_alert.risk_level == RiskLevel.CRITICAL
    assert "EXPEDITE AIR FREIGHT" in result.risk_alert.recommended_action
    assert result.lead_time_variance_days > supplier.lead_time_days

def test_monte_carlo_simulation_output():
    """
    Verifies that the Monte Carlo simulator calculates realistic probabilities.
    """
    sku = SKUInventory(
        sku="TEST-SKU-002",
        name="Stable Component",
        current_stock=5000,
        daily_burn_rate=50,
        primary_supplier_id="SUP-TEST-02"
    )
    supplier = SupplierData(
        supplier_id="SUP-TEST-02",
        name="Stable Supplier",
        country="Germany",
        historical_otif_rate=0.98,
        lead_time_days=10,
        geopolitical_risk_index=0.10
    )
    
    sim_result = MonteCarloSimulator.run_lead_time_simulation(sku, supplier, iterations=500)
    
    assert sim_result.iterations == 500
    assert sim_result.stockout_probability_pct == 0.0  # Should have near-zero risk
    assert sim_result.p95_worst_case_lead_days >= supplier.lead_time_days
