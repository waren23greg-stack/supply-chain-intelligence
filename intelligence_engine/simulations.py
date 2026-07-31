import numpy as np
from pydantic import BaseModel
from intelligence_engine.schemas import SKUInventory, SupplierData

class SimulationResult(BaseModel):
    sku: str
    supplier_id: str
    iterations: int
    stockout_probability_pct: float
    expected_lead_time_days: float
    p95_worst_case_lead_days: float
    mean_days_until_stockout: float
    recommended_safety_stock_buffer: int

class MonteCarloSimulator:
    @staticmethod
    def run_lead_time_simulation(
        sku: SKUInventory,
        supplier: SupplierData,
        iterations: int = 1000,
        demand_volatility: float = 0.15
    ) -> SimulationResult:
        """
        Runs Monte Carlo simulations combining lead-time volatility and demand fluctuations.
        """
        np.random.seed(42)  # For reproducible enterprise reporting
        
        # 1. Model Lead Time Volatility (Log-Normal distribution based on OTIF and Geopolitical Risk)
        base_lead = supplier.lead_time_days
        risk_factor = supplier.geopolitical_risk_index + (1.0 - supplier.historical_otif_rate)
        scale_param = max(0.05, risk_factor * 0.4)
        
        simulated_lead_times = np.random.lognormal(
            mean=np.log(base_lead),
            sigma=scale_param,
            size=iterations
        )
        
        # 2. Model Daily Demand Volatility (Normal distribution)
        simulated_daily_burns = np.random.normal(
            loc=sku.daily_burn_rate,
            scale=sku.daily_burn_rate * demand_volatility,
            size=iterations
        )
        simulated_daily_burns = np.maximum(simulated_daily_burns, 1.0)  # Prevent zero/negative demand
        
        # 3. Calculate Stockout Events across iterations
        total_available_stock = sku.current_stock + sku.in_transit_qty
        days_of_inventory = total_available_stock / simulated_daily_burns
        
        # A stockout occurs if simulated lead time exceeds our days of inventory
        stockout_events = simulated_lead_times > days_of_inventory
        stockout_probability = (np.sum(stockout_events) / iterations) * 100.0
        
        # 4. Calculate Key Statistical Metrics
        p95_lead = float(np.percentile(simulated_lead_times, 95))
        expected_lead = float(np.mean(simulated_lead_times))
        mean_stockout_days = float(np.mean(days_of_inventory))
        
        # Safety stock needed to survive the 95th percentile worst-case lead time
        required_safety_stock = int(p95_lead * sku.daily_burn_rate)
        
        return SimulationResult(
            sku=sku.sku,
            supplier_id=supplier.supplier_id,
            iterations=iterations,
            stockout_probability_pct=round(stockout_probability, 2),
            expected_lead_time_days=round(expected_lead, 1),
            p95_worst_case_lead_days=round(p95_lead, 1),
            mean_days_until_stockout=round(mean_stockout_days, 1),
            recommended_safety_stock_buffer=required_safety_stock
        )
