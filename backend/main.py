from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from intelligence_engine.schemas import SupplyChainState, SKUInventory, SupplierData
from intelligence_engine.agents import run_supply_chain_pipeline
from intelligence_engine.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multi-Agent Supply Chain Intelligence Engine API"
)

# Enable CORS for front-end decision dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "operational", "engine": settings.APP_NAME}

@app.post("/api/v1/analyze-sku-risk", response_model=SupplyChainState)
def analyze_sku_risk(payload: SupplyChainState):
    """
    Runs an SKU and its associated supplier through the multi-agent intelligence pipeline.
    """
    try:
        evaluated_state = run_supply_chain_pipeline(payload)
        return evaluated_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence pipeline error: {str(e)}")

# Sample Endpoint for Quick Testing / Demo
@app.get("/api/v1/demo-scenario")
def get_demo_scenario():
    """
    Returns a simulated high-risk semiconductor disruption scenario.
    """
    sample_sku = SKUInventory(
        sku="IC-ARM-992",
        name="Automotive Microcontroller Unit",
        current_stock=1200,
        daily_burn_rate=80,
        primary_supplier_id="SUP-TWN-01",
        in_transit_qty=400
    )
    sample_supplier = SupplierData(
        supplier_id="SUP-TWN-01",
        name="Taipei Silicon Precision",
        country="Taiwan",
        historical_otif_rate=0.78,
        lead_time_days=18,
        geopolitical_risk_index=0.65
    )
    initial_state = SupplyChainState(sku_data=sample_sku, supplier_data=sample_supplier)
    return run_supply_chain_pipeline(initial_state)
