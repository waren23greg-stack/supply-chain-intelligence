import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  ShieldCheck, 
  Truck, 
  Package, 
  RefreshCw, 
  Activity, 
  ArrowUpRight, 
  Sliders 
} from 'lucide-react';

const API_BASE_URL = "http://localhost:8000/api/v1";

export default function SupplyChainDashboard() {
  const [skuData, setSkuData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSku, setSelectedSku] = useState(null);
  
  // What-If Simulator Form State
  const [simState, setSimState] = useState({
    supplier_code: 'SUP-TWN-01',
    severity: 0.85,
    delay_days: 12,
    disruption_type: 'PORT_CONGESTION'
  });
  const [simLoading, setSimLoading] = useState(false);

  // Fetch initial risks from PostgreSQL backend
  const fetchRiskData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/all-risks`);
      if (response.ok) {
        const data = await response.json();
        setSkuData(data);
        if (data.length > 0) setSelectedSku(data[0]);
      } else {
        // Fallback demo data if API is unattached
        useFallbackData();
      }
    } catch (err) {
      console.warn("API offline, rendering fallback demo state:", err);
      useFallbackData();
    } finally {
      setLoading(false);
    }
  };

  const useFallbackData = () => {
    const fallback = [
      {
        sku_data: { sku: "IC-ARM-992", name: "Automotive Microcontroller Unit", current_stock: 1200, daily_burn_rate: 80, in_transit_qty: 400 },
        supplier_data: { name: "Taipei Silicon Precision", country: "Taiwan", historical_otif_rate: 0.78, lead_time_days: 18, geopolitical_risk_index: 0.65 },
        lead_time_variance_days: 22,
        risk_alert: { sku: "IC-ARM-992", risk_level: "CRITICAL", projected_stockout_days: 15, root_cause: "Effective lead time (22d) exceeds stock buffer (15d).", recommended_action: "EXPEDITE AIR FREIGHT: Order emergency lot of 1,120 units." }
      },
      {
        sku_data: { sku: "DRV-SRV-104", name: "High-Torque Precision Servo", current_stock: 450, daily_burn_rate: 15, in_transit_qty: 0 },
        supplier_data: { name: "Bavarian Industrial Drives", country: "Germany", historical_otif_rate: 0.96, lead_time_days: 10, geopolitical_risk_index: 0.15 },
        lead_time_variance_days: 10,
        risk_alert: { sku: "DRV-SRV-104", risk_level: "LOW", projected_stockout_days: 30, root_cause: "Inventory levels exceed risk thresholds.", recommended_action: "OPTIMAL: Maintain standard replenishment cycle." }
      }
    ];
    setSkuData(fallback);
    setSelectedSku(fallback[0]);
  };

  useEffect(() => {
    fetchRiskData();
  }, []);

  // Trigger real-time disruption webhook simulation
  const handleTriggerWebhook = async (e) => {
    e.preventDefault();
    setSimLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/webhooks/supplier-alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_code: simState.supplier_code,
          disruption_type: simState.disruption_type,
          severity: parseFloat(simState.severity),
          estimated_delay_days: parseInt(simState.delay_days),
          message: `Simulated disruption test via Executive Dashboard`
        })
      });
      if (res.ok) {
        await fetchRiskData();
      }
    } catch (err) {
      alert("Webhook simulated locally!");
    } finally {
      setSimLoading(false);
    }
  };

  // Aggregated KPI Stats
  const totalSKUs = skuData.length;
  const criticalCount = skuData.filter(s => s.risk_alert?.risk_level === 'CRITICAL').length;
  const highRiskCount = skuData.filter(s => s.risk_alert?.risk_level === 'HIGH').length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      {/* Top Executive Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 pb-4 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="text-blue-500 w-7 h-7" />
            Supply Chain Intelligence Control Tower
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time multi-agent risk modeling & dynamic inventory simulation
          </p>
        </div>
        <button
          onClick={fetchRiskData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Pipeline
        </button>
      </header>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-sm mb-2">
            <span>Total Tracked SKUs</span>
            <Package className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{totalSKUs}</div>
          <div className="text-xs text-slate-500 mt-1">Synchronized with ERP</div>
        </div>

        <div className="bg-slate-900/80 border border-red-900/40 p-5 rounded-xl">
          <div className="flex justify-between items-center text-red-400 text-sm mb-2">
            <span>Critical Stockouts</span>
            <AlertTriangle className="w-5 h-5 text-red-500" />
          </div>
          <div className="text-3xl font-extrabold text-red-400">{criticalCount}</div>
          <div className="text-xs text-red-400/70 mt-1">Requires immediate air-freight</div>
        </div>

        <div className="bg-slate-900/80 border border-amber-900/40 p-5 rounded-xl">
          <div className="flex justify-between items-center text-amber-400 text-sm mb-2">
            <span>High Risk Lead Times</span>
            <Truck className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">{highRiskCount}</div>
          <div className="text-xs text-amber-400/70 mt-1">Buffer depletion in &lt; 14 days</div>
        </div>

        <div className="bg-slate-900/80 border border-emerald-900/40 p-5 rounded-xl">
          <div className="flex justify-between items-center text-emerald-400 text-sm mb-2">
            <span>Optimal Logistics</span>
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">
            {totalSKUs - criticalCount - highRiskCount}
          </div>
          <div className="text-xs text-emerald-400/70 mt-1">Operating within thresholds</div>
        </div>
      </div>

      {/* Main Grid: SKU Inventory Risk Table + Disruption Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* SKU Risk Scorecard Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-400" />
            Inventory Risk Scorecard
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3">SKU</th>
                  <th className="p-3">Item Name</th>
                  <th className="p-3">Supplier</th>
                  <th className="p-3">Risk Level</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {skuData.map((item, idx) => {
                  const risk = item.risk_alert?.risk_level || 'LOW';
                  return (
                    <tr 
                      key={idx} 
                      onClick={() => setSelectedSku(item)}
                      className={`hover:bg-slate-800/50 cursor-pointer transition ${
                        selectedSku?.sku_data.sku === item.sku_data.sku ? 'bg-slate-800/80' : ''
                      }`}
                    >
                      <td className="p-3 font-mono font-semibold text-blue-400">{item.sku_data.sku}</td>
                      <td className="p-3 text-white font-medium">{item.sku_data.name}</td>
                      <td className="p-3 text-slate-400">{item.supplier_data.name}</td>
                      <td className="p-3">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          risk === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' :
                          risk === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                          'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        }`}>
                          {risk}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <button className="text-slate-400 hover:text-white inline-flex items-center gap-1 text-xs">
                          Inspect <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Detailed Agent Breakdown Drawer */}
          {selectedSku && (
            <div className="mt-6 p-5 bg-slate-950 border border-slate-800 rounded-lg">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="text-xs text-blue-400 font-mono">{selectedSku.sku_data.sku}</span>
                  <h3 className="text-base font-bold text-white">{selectedSku.sku_data.name}</h3>
                </div>
                <span className="text-xs text-slate-500">
                  Lead Time Inflated to {selectedSku.lead_time_variance_days} Days
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-xs mb-4 text-slate-400">
                <div>Current Stock: <strong className="text-white">{selectedSku.sku_data.current_stock} units</strong></div>
                <div>Daily Burn Rate: <strong className="text-white">{selectedSku.sku_data.daily_burn_rate} units/day</strong></div>
                <div>Primary Supplier: <strong className="text-white">{selectedSku.supplier_data.name} ({selectedSku.supplier_data.country})</strong></div>
                <div>OTIF History: <strong className="text-white">{(selectedSku.supplier_data.historical_otif_rate * 100).toFixed(0)}%</strong></div>
              </div>
              <div className="p-3 bg-red-950/30 border border-red-900/50 rounded text-xs text-red-300">
                <strong>Agent Recommendation:</strong> {selectedSku.risk_alert?.recommended_action}
              </div>
            </div>
          )}
        </div>

        {/* What-If Disruption Simulator Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            What-If Disruption Simulator
          </h2>
          <p className="text-xs text-slate-400 mb-6">
            Inject real-time port or geopolitical disruption webhooks to test multi-agent resilience.
          </p>

          <form onSubmit={handleTriggerWebhook} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Target Supplier</label>
              <select
                value={simState.supplier_code}
                onChange={e => setSimState({...simState, supplier_code: e.target.value})}
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
              >
                <option value="SUP-TWN-01">SUP-TWN-01 (Taipei Silicon Precision)</option>
                <option value="SUP-GER-02">SUP-GER-02 (Bavarian Industrial Drives)</option>
                <option value="SUP-VNM-03">SUP-VNM-03 (Mekong Electronics)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Disruption Event</label>
              <select
                value={simState.disruption_type}
                onChange={e => setSimState({...simState, disruption_type: e.target.value})}
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
              >
                <option value="PORT_CONGESTION">Port Congestion / Strike</option>
                <option value="GEOPOLITICAL">Geopolitical Conflict</option>
                <option value="WEATHER">Typhoon / Extreme Weather</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">
                Disruption Severity (Risk Index: {simState.severity})
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.05"
                value={simState.severity}
                onChange={e => setSimState({...simState, severity: e.target.value})}
                className="w-full accent-blue-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Expected Delay Inflation (Days)</label>
              <input
                type="number"
                value={simState.delay_days}
                onChange={e => setSimState({...simState, delay_days: e.target.value})}
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
              />
            </div>

            <button
              type="submit"
              disabled={simLoading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition text-xs flex justify-center items-center gap-2"
            >
              {simLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Simulate Disruption Alert'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
