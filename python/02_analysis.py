# ============================================================
#   SUPPLY CHAIN INTELLIGENCE PLATFORM
#   Python Analysis & Forecasting Engine
#   Author  : Supply Chain Intelligence Team
#   Requires: pandas, matplotlib, seaborn, scikit-learn,
#             mysql-connector-python, sqlalchemy
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sqlalchemy import create_engine
import warnings
import os
from datetime import datetime

warnings.filterwarnings("ignore")

# ============================================================
# CONFIG
# ============================================================
DB_USER     = "root"
DB_PASSWORD = "waren23.greg%40student.cuk.ac.ke"
DB_HOST     = "localhost"
DB_NAME     = "supply_chain"
OUTPUT_DIR  = "../data/clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("../docs/charts", exist_ok=True)

print("=" * 60)
print("  SUPPLY CHAIN INTELLIGENCE — ANALYSIS ENGINE")
print("=" * 60)

# ============================================================
# 1. CONNECT & LOAD DATA
# ============================================================
print("\n[1/7] Connecting to MySQL and loading data...")

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

suppliers  = pd.read_sql("SELECT * FROM suppliers",  engine)
products   = pd.read_sql("SELECT * FROM products",   engine)
inventory  = pd.read_sql("SELECT * FROM inventory",  engine)
orders     = pd.read_sql("SELECT * FROM orders",     engine)
shipments  = pd.read_sql("SELECT * FROM shipments",  engine)

orders["order_date"]        = pd.to_datetime(orders["order_date"])
orders["expected_delivery"] = pd.to_datetime(orders["expected_delivery"])
shipments["actual_delivery"] = pd.to_datetime(shipments["actual_delivery"])

print(f"  ✅ Suppliers  : {len(suppliers):,} rows")
print(f"  ✅ Products   : {len(products):,} rows")
print(f"  ✅ Inventory  : {len(inventory):,} rows")
print(f"  ✅ Orders     : {len(orders):,} rows")
print(f"  ✅ Shipments  : {len(shipments):,} rows")

# ============================================================
# 2. EXPLORATORY DATA ANALYSIS
# ============================================================
print("\n[2/7] Running Exploratory Data Analysis...")

# --- Merge master dataset ---
master = (
    orders
    .merge(products,   on="product_id",   suffixes=("", "_prod"))
    .merge(suppliers,  on="supplier_id",  suffixes=("", "_sup"))
    .merge(shipments,  on="order_id",     how="left")
    .merge(inventory,  on="product_id",   how="left", suffixes=("", "_inv"))
)

master["revenue"] = master["quantity_ordered"] * master["unit_price"]
master["month"]   = master["order_date"].dt.to_period("M")

# --- Monthly revenue ---
monthly_revenue = (
    master[master["status"] != "Cancelled"]
    .groupby("month")["revenue"]
    .sum()
    .reset_index()
)
monthly_revenue["month_dt"] = monthly_revenue["month"].dt.to_timestamp()

# --- Category revenue ---
cat_revenue = (
    master[master["status"] != "Cancelled"]
    .groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# --- Carrier performance ---
carrier_perf = (
    shipments.groupby("carrier")
    .agg(
        total=("shipment_id", "count"),
        on_time=("shipment_status", lambda x: (x == "On Time").sum()),
        avg_delay=("delay_days", "mean")
    )
    .reset_index()
)
carrier_perf["on_time_pct"] = (
    carrier_perf["on_time"] / carrier_perf["total"] * 100
).round(1)

# --- Inventory health ---
inv_merged = inventory.merge(products, on="product_id")
inv_merged["stock_status"] = inv_merged.apply(
    lambda r: "Out of Stock" if r["quantity_in_stock"] == 0
    else "Critical"   if r["quantity_in_stock"] <= r["reorder_level"] * 0.5
    else "Reorder"    if r["quantity_in_stock"] <= r["reorder_level"]
    else "Adequate"   if r["quantity_in_stock"] <= r["reorder_level"] * 1.5
    else "Healthy",
    axis=1
)
stock_counts = inv_merged["stock_status"].value_counts().reset_index()
stock_counts.columns = ["status", "count"]

print("  ✅ EDA complete")

# ============================================================
# 3. DEMAND FORECASTING (Linear Trend)
# ============================================================
print("\n[3/7] Running demand forecasting...")

from sklearn.linear_model import LinearRegression

# Use only complete months (exclude current partial month)
monthly_clean = monthly_revenue[
    monthly_revenue["month_dt"] < monthly_revenue["month_dt"].max()
].copy()

monthly_clean["t"] = np.arange(len(monthly_clean))
X = monthly_clean[["t"]]
y = monthly_clean["revenue"]

model = LinearRegression()
model.fit(X, y)
monthly_clean["predicted"] = model.predict(X)

# Forecast next 3 months
last_t    = monthly_clean["t"].max()
last_date = monthly_clean["month_dt"].max()
future_ts = [last_t + i for i in range(1, 4)]
future_dates = pd.date_range(last_date, periods=4, freq="MS")[1:]
forecast_values = model.predict(np.array(future_ts).reshape(-1, 1))

forecast_df = pd.DataFrame({
    "month_dt"  : future_dates,
    "revenue"   : [None] * 3,
    "predicted" : forecast_values,
    "forecast"  : True
})
monthly_clean["forecast"] = False
forecast_full = pd.concat([monthly_clean, forecast_df], ignore_index=True)

print(f"  ✅ Forecast complete")
print(f"     Next 3 months predicted revenue:")
for d, v in zip(future_dates, forecast_values):
    print(f"     {d.strftime('%b %Y')} → ${v:,.2f}")

# ============================================================
# 4. SUPPLIER SCORECARD
# ============================================================
print("\n[4/7] Building supplier scorecard...")

supplier_score = (
    master.groupby(["supplier_id", "supplier_name", "country", "rating"])
    .agg(
        total_orders=("order_id", "count"),
        total_revenue=("revenue", "sum"),
        avg_delay=("delay_days", "mean"),
        on_time=("shipment_status", lambda x: (x == "On Time").sum()),
        total_shipments=("shipment_id", "count")
    )
    .reset_index()
)
supplier_score["on_time_pct"] = (
    supplier_score["on_time"] / supplier_score["total_shipments"] * 100
).round(1)
supplier_score["performance_tier"] = supplier_score["on_time_pct"].apply(
    lambda x: "ELITE"    if x >= 85
    else       "RELIABLE" if x >= 65
    else       "AVERAGE"  if x >= 45
    else       "AT RISK"
)
supplier_score = supplier_score.sort_values("on_time_pct", ascending=False)

print("  ✅ Supplier scorecard built")

# ============================================================
# 5. STOCKOUT ALERT REPORT
# ============================================================
print("\n[5/7] Generating stockout alert report...")

stockout_alert = (
    inv_merged[inv_merged["quantity_in_stock"] <= inv_merged["reorder_level"]]
    .merge(suppliers[["supplier_id", "supplier_name", "lead_time_days"]],
           on="supplier_id")
    .assign(
        units_short=lambda df: df["reorder_level"] - df["quantity_in_stock"],
        reorder_cost=lambda df: df["units_short"] * df["unit_price"],
        earliest_restock=lambda df: pd.Timestamp.today().normalize()
            + pd.to_timedelta(df["lead_time_days"], unit="d")
    )
    [[
        "product_name", "category", "supplier_name", "lead_time_days",
        "quantity_in_stock", "reorder_level", "units_short",
        "unit_price", "reorder_cost", "earliest_restock"
    ]]
    .sort_values("reorder_cost", ascending=False)
)

print(f"  ✅ {len(stockout_alert)} products need reordering")
print(f"     Total reorder cost: ${stockout_alert['reorder_cost'].sum():,.2f}")

# ============================================================
# 6. VISUALIZATIONS
# ============================================================
print("\n[6/7] Generating charts...")

sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({
    "figure.facecolor" : "#0d1117",
    "axes.facecolor"   : "#161b22",
    "axes.labelcolor"  : "#c9d1d9",
    "xtick.color"      : "#8b949e",
    "ytick.color"      : "#8b949e",
    "text.color"       : "#c9d1d9",
    "grid.color"       : "#21262d",
    "axes.titlecolor"  : "#58a6ff",
    "axes.titlesize"   : 11,
    "axes.titleweight" : "bold",
})

fig = plt.figure(figsize=(20, 16), facecolor="#0d1117")
fig.suptitle(
    "SUPPLY CHAIN INTELLIGENCE — ANALYTICS DASHBOARD",
    fontsize=16, fontweight="bold", color="#58a6ff", y=0.98
)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

GREEN  = "#00ff88"
BLUE   = "#58a6ff"
AMBER  = "#ffa657"
RED    = "#ff7b72"
PURPLE = "#bc8cff"
COLORS = [GREEN, BLUE, AMBER, RED, PURPLE]

# --- Chart 1: Monthly Revenue + Forecast ---
ax1 = fig.add_subplot(gs[0, :2])
hist = forecast_full[forecast_full["forecast"] == False]
fcast = forecast_full[forecast_full["forecast"] == True]
hist_rev = hist["revenue"].astype(float) / 1e6
ax1.fill_between(hist["month_dt"], hist_rev,
                 alpha=0.15, color=GREEN)
ax1.plot(hist["month_dt"], hist_rev,
         color=GREEN, linewidth=2, label="Actual Revenue")
ax1.plot(hist["month_dt"], hist["predicted"] / 1e6,
         color=BLUE, linewidth=1.5, linestyle="--", label="Trend Line")
ax1.plot(fcast["month_dt"], fcast["predicted"] / 1e6,
         color=AMBER, linewidth=2, linestyle="--", marker="o",
         markersize=7, label="3-Month Forecast")
ax1.axvline(hist["month_dt"].max(), color="#444", linestyle=":", linewidth=1)
ax1.set_title("Monthly Revenue & 3-Month Forecast")
ax1.set_ylabel("Revenue (USD Millions)")
ax1.legend(facecolor="#161b22", edgecolor="#333", labelcolor="#c9d1d9",
           fontsize=8)

# --- Chart 2: Revenue by Category (donut) ---
ax2 = fig.add_subplot(gs[0, 2])
wedges, texts, autotexts = ax2.pie(
    cat_revenue["revenue"],
    labels=cat_revenue["category"],
    autopct="%1.1f%%",
    colors=COLORS,
    startangle=90,
    pctdistance=0.75,
    wedgeprops=dict(width=0.5, edgecolor="#0d1117", linewidth=2)
)
for t in texts:     t.set_color("#c9d1d9"); t.set_fontsize(8)
for t in autotexts: t.set_color("#0d1117"); t.set_fontsize(8); t.set_fontweight("bold")
ax2.set_title("Revenue Share by Category")

# --- Chart 3: Carrier Reliability ---
ax3 = fig.add_subplot(gs[1, 0])
bars = ax3.barh(carrier_perf["carrier"], carrier_perf["on_time_pct"],
                color=[GREEN if x >= 40 else RED for x in carrier_perf["on_time_pct"]],
                edgecolor="#0d1117", linewidth=0.5)
ax3.set_xlim(0, 50)
ax3.set_title("Carrier On-Time Rate (%)")
ax3.set_xlabel("On-Time %")
for bar, val in zip(bars, carrier_perf["on_time_pct"]):
    ax3.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val}%", va="center", fontsize=8, color="#c9d1d9")

# --- Chart 4: Inventory Health ---
ax4 = fig.add_subplot(gs[1, 1])
color_map = {
    "Healthy": GREEN, "Adequate": BLUE,
    "Reorder": AMBER, "Critical": RED, "Out of Stock": "#ff0000"
}
bar_colors = [color_map.get(s, BLUE) for s in stock_counts["status"]]
ax4.bar(stock_counts["status"], stock_counts["count"],
        color=bar_colors, edgecolor="#0d1117", linewidth=0.5)
ax4.set_title("Inventory Health Distribution")
ax4.set_ylabel("Product Count")
ax4.tick_params(axis="x", rotation=20)
for i, v in enumerate(stock_counts["count"]):
    ax4.text(i, v + 1, str(v), ha="center", fontsize=9, color="#c9d1d9")

# --- Chart 5: Top 10 Suppliers by On-Time % ---
ax5 = fig.add_subplot(gs[1, 2])
top_sup = supplier_score.head(10)
ax5.barh(top_sup["supplier_name"].str[:18],
         top_sup["on_time_pct"],
         color=BLUE, edgecolor="#0d1117", linewidth=0.5)
ax5.set_title("Top 10 Suppliers (On-Time %)")
ax5.set_xlabel("On-Time %")
ax5.invert_yaxis()

# --- Chart 6: Monthly Order Volume ---
ax6 = fig.add_subplot(gs[2, :2])
monthly_orders = master.groupby("month")["order_id"].count().reset_index()
monthly_orders["month_dt"] = monthly_orders["month"].dt.to_timestamp()
ax6.fill_between(monthly_orders["month_dt"], monthly_orders["order_id"],
                 alpha=0.2, color=PURPLE)
ax6.plot(monthly_orders["month_dt"], monthly_orders["order_id"],
         color=PURPLE, linewidth=2)
ax6.set_title("Monthly Order Volume")
ax6.set_ylabel("Number of Orders")

# --- Chart 7: Delay Distribution by Carrier ---
ax7 = fig.add_subplot(gs[2, 2])
ship_merged = shipments.copy()
for carrier in shipments["carrier"].unique():
    data = shipments[shipments["carrier"] == carrier]["delay_days"]
    ax7.plot(sorted(data), np.linspace(0, 1, len(data)),
             label=carrier, linewidth=1.5)
ax7.set_title("Delay Distribution by Carrier (CDF)")
ax7.set_xlabel("Delay Days")
ax7.set_ylabel("Cumulative Probability")
ax7.legend(facecolor="#161b22", edgecolor="#333",
           labelcolor="#c9d1d9", fontsize=7)

chart_path = "../docs/charts/supply_chain_dashboard.png"
plt.savefig(chart_path, dpi=150, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()
print(f"  ✅ Dashboard chart saved → {chart_path}")

# ============================================================
# 7. EXPORT CLEAN CSVs FOR POWER BI
# ============================================================
print("\n[7/7] Exporting clean CSVs for Power BI...")

# 7A. Master orders dataset
master_export = master[[
    "order_id", "order_date", "month", "status",
    "product_name", "category", "unit_price",
    "quantity_ordered", "revenue",
    "supplier_name", "country", "rating",
    "shipment_status", "delay_days", "carrier",
    "warehouse_location", "quantity_in_stock"
]].copy()
master_export["month"] = master_export["month"].astype(str)
master_export.to_csv(f"{OUTPUT_DIR}/master_orders.csv", index=False)
print(f"  ✅ master_orders.csv        ({len(master_export):,} rows)")

# 7B. Monthly revenue + forecast
forecast_export = forecast_full[[
    "month_dt", "revenue", "predicted", "forecast"
]].copy()
forecast_export["month_dt"] = forecast_export["month_dt"].astype(str)
forecast_export.to_csv(f"{OUTPUT_DIR}/monthly_revenue_forecast.csv", index=False)
print(f"  ✅ monthly_revenue_forecast.csv ({len(forecast_export):,} rows)")

# 7C. Supplier scorecard
supplier_score.to_csv(f"{OUTPUT_DIR}/supplier_scorecard.csv", index=False)
print(f"  ✅ supplier_scorecard.csv   ({len(supplier_score):,} rows)")

# 7D. Stockout alerts
stockout_alert["earliest_restock"] = stockout_alert["earliest_restock"].astype(str)
stockout_alert.to_csv(f"{OUTPUT_DIR}/stockout_alerts.csv", index=False)
print(f"  ✅ stockout_alerts.csv      ({len(stockout_alert):,} rows)")

# 7E. Inventory health
inv_export = inv_merged[[
    "product_id", "product_name", "category", "unit_price",
    "reorder_level", "warehouse_location",
    "quantity_in_stock", "stock_status"
]].copy()
inv_export["stock_value"] = inv_export["quantity_in_stock"] * inv_export["unit_price"]
inv_export.to_csv(f"{OUTPUT_DIR}/inventory_health.csv", index=False)
print(f"  ✅ inventory_health.csv     ({len(inv_export):,} rows)")

# 7F. Carrier performance
carrier_perf.to_csv(f"{OUTPUT_DIR}/carrier_performance.csv", index=False)
print(f"  ✅ carrier_performance.csv  ({len(carrier_perf):,} rows)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("  ANALYSIS COMPLETE")
print("=" * 60)
print(f"  Total Revenue    : ${master['revenue'].sum():>15,.2f}")
print(f"  Total Orders     : {len(orders):>15,}")
print(f"  Active Suppliers : {len(suppliers):>15,}")
print(f"  Products at Risk : {len(stockout_alert):>15,}")
print(f"  Avg Delay (days) : {shipments['delay_days'].mean():>15.2f}")
print(f"  CSVs exported to : {OUTPUT_DIR}")
print(f"  Chart saved to   : ../docs/charts/")
print("=" * 60)
print("\n🚀 Ready for Power BI — connect to data/clean/*.csv")