import math
from typing import Dict, Any
from intelligence_engine.schemas import (
    SupplyChainState, RiskLevel, AgentRiskAlert
)

class SupplyChainAgents:
    @staticmethod
    def market_signal_agent(state: SupplyChainState) -> SupplyChainState:
        """
        Analyzes geopolitical and market conditions to estimate supply shocks.
        """
        risk = state.supplier_data.geopolitical_risk_index
        otif = state.supplier_data.historical_otif_rate
        
        # Simulated external disruption signal processing
        disruption_penalty = 0
        if risk > 0.6 or otif < 0.85:
            disruption_penalty = math.ceil((1.0 - otif) * 14) # Up to 14 days delay
            
        state.market_signals["port_congestion_warning"] = risk > 0.5
        state.market_signals["disruption_penalty_days"] = disruption_penalty
        return state

    @staticmethod
    def logistics_agent(state: SupplyChainState) -> SupplyChainState:
        """
        Calculates realistic lead time adjustments based on market signals.
        """
        base_lead = state.supplier_data.lead_time_days
        penalty = state.market_signals.get("disruption_penalty_days", 0)
        
        state.lead_time_variance_days = base_lead + penalty
        return state

    @staticmethod
    def inventory_strategist_agent(state: SupplyChainState) -> SupplyChainState:
        """
        Determines stockout probability and recommends executive action.
        """
        stock = state.sku_data.current_stock
        burn = state.sku_data.daily_burn_rate
        transit = state.sku_data.in_transit_qty
        effective_lead = state.lead_time_variance_days
        
        days_of_stock = stock / burn if burn > 0 else 999
        total_days_with_transit = (stock + transit) / burn if burn > 0 else 999
        
        # Risk Evaluation
        if days_of_stock <= effective_lead:
            level = RiskLevel.CRITICAL if (effective_lead - days_of_stock) > 5 else RiskLevel.HIGH
            action = f"EXPEDITE AIR FREIGHT: Order emergency lot of {burn * (effective_lead - int(days_of_stock) + 7)} units."
            cause = f"Effective lead time ({effective_lead}d) exceeds current stock buffer ({int(days_of_stock)}d)."
        elif total_days_with_transit <= effective_lead:
            level = RiskLevel.MODERATE
            action = "MONITOR: In-transit shipment required to avoid stockout. Check carrier ETA."
            cause = "Safety stock buffer depleted; relying on transit cargo."
        else:
            level = RiskLevel.LOW
            action = "OPTIMAL: Maintain standard replenishment cycle."
            cause = "Inventory levels exceed risk thresholds."

        state.risk_alert = AgentRiskAlert(
            sku=state.sku_data.sku,
            risk_level=level,
            projected_stockout_days=int(days_of_stock),
            root_cause=cause,
            recommended_action=action
        )
        return state

def run_supply_chain_pipeline(state: SupplyChainState) -> SupplyChainState:
    """
    Sequential execution pipeline simulating a LangGraph workflow.
    """
    state = SupplyChainAgents.market_signal_agent(state)
    state = SupplyChainAgents.logistics_agent(state)
    state = SupplyChainAgents.inventory_strategist_agent(state)
    return state
