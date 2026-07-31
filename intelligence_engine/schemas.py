from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SupplierData(BaseModel):
    supplier_id: str
    name: str
    country: str
    historical_otif_rate: float = Field(..., description="On-Time In-Full delivery percentage (0-1)")
    lead_time_days: int
    geopolitical_risk_index: float = Field(0.2, description="0 (safe) to 1.0 (high risk)")

class SKUInventory(BaseModel):
    sku: str
    name: str
    current_stock: int
    daily_burn_rate: int
    primary_supplier_id: str
    in_transit_qty: int = 0

class AgentRiskAlert(BaseModel):
    sku: str
    risk_level: RiskLevel
    projected_stockout_days: int
    root_cause: str
    recommended_action: str

# LangGraph Shared State
class SupplyChainState(BaseModel):
    sku_data: SKUInventory
    supplier_data: SupplierData
    market_signals: Dict[str, Any] = {}
    lead_time_variance_days: int = 0
    risk_alert: Optional[AgentRiskAlert] = None
