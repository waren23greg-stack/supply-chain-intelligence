# 🏭 Supply Chain Intelligence Platform

> An end-to-end supply chain analytics system built with **MySQL**, **Python**, and **Power BI** — simulating real-world business intelligence workflows used by data analysts in logistics, procurement, and operations.

---

## 📌 Project Overview

This project demonstrates a full data analytics pipeline applied to supply chain management. Starting from raw database design through to automated analysis, forecasting, and interactive dashboards — every layer reflects skills directly relevant to data analyst and business intelligence roles.

**The core question this project answers:**
> *How can raw transactional data be transformed into actionable insights that drive smarter supply chain decisions?*

---

## 🧱 Architecture

```
MySQL Database  ──►  Python Analysis Engine  ──►  Power BI Dashboard
(Raw Data)            (Clean, Analyze, Forecast)    (Visualize & Report)
     │                         │                            │
  5 Tables               6 CSV Exports               5 Dashboard Pages
 9,450 Rows           EDA + Forecasting            Executive KPIs + Drilldowns
18 SQL Queries         Chart Generation             Supplier & Inventory Views
```

---

## 🗂️ Repository Structure

```
supply-chain-intelligence/
│
├── sql/
│   ├── 01_create_schema.sql        # Database schema — 5 relational tables
│   └── 02_analytics_queries.sql    # 18 advanced analytics queries
│
├── python/
│   ├── 01_data_generator.py        # Generates 9,450 rows of realistic data
│   └── 02_analysis.py              # EDA, forecasting, charts, CSV exports
│
├── js/
│   ├── server.js                   # Node.js + Express backend
│   ├── index.html                  # Browser-based data generator UI
│   └── package.json                # JS dependencies
│
├── data/
│   ├── raw/                        # Source data
│   └── clean/                      # Processed CSVs for Power BI
│       ├── master_orders.csv
│       ├── monthly_revenue_forecast.csv
│       ├── supplier_scorecard.csv
│       ├── stockout_alerts.csv
│       ├── inventory_health.csv
│       └── carrier_performance.csv
│
├── powerbi/
│   └── supply_chain_dashboard.pbix # Interactive Power BI dashboard
│
├── docs/
│   └── charts/
│       └── supply_chain_dashboard.png  # Python-generated analytics chart
│
└── README.md
```

---

## 🗄️ Database Schema

Five relational tables modeling a realistic supply chain:

| Table | Rows | Description |
|---|---|---|
| `suppliers` | 50 | Supplier profiles, ratings, lead times, countries |
| `products` | 200 | Product catalog with categories and pricing |
| `inventory` | 200 | Stock levels across 4 warehouse locations |
| `orders` | 5,000 | Purchase orders with status and delivery dates |
| `shipments` | 4,000 | Shipment records with delay tracking per carrier |

**Total: 9,450 rows across 5 tables**

---

## 🔍 SQL Analytics (18 Queries)

Organized into 6 analytical sections:

| Section | Queries | Techniques |
|---|---|---|
| Supplier Scorecard | 3 | JOINs, CASE WHEN, aggregations, performance tiers |
| Inventory Health | 4 | Stock status logic, warehouse value, turnover ratios |
| Shipment Delay Analysis | 3 | Carrier leaderboard, monthly trends, cost impact |
| Order & Revenue Trends | 4 | Monthly revenue, category breakdown, top products |
| Executive KPI Summary | 1 | Single-query full business snapshot |
| Advanced Window Functions | 3 | CTEs, RANK(), LAG(), running totals, cumulative revenue |

---

## 🐍 Python Analysis Engine

**`01_data_generator.py`** — Synthetic data generation using Faker, random, and mysql-connector. Populates all 5 tables with realistic supply chain data.

**`02_analysis.py`** — Full analytics pipeline:

- Connects to MySQL via SQLAlchemy and loads all tables into pandas DataFrames
- Merges datasets into a master analytics table
- Performs Exploratory Data Analysis (EDA) across suppliers, products, and shipments
- Builds a **Linear Regression demand forecast** for the next 3 months using scikit-learn
- Generates a **7-panel analytics dashboard** using matplotlib and seaborn
- Exports **6 clean CSV files** ready for Power BI ingestion

**Sample forecast output:**
```
Mar 2026 → $2,196,398
Apr 2026 → $2,201,960
May 2026 → $2,207,522
```

**Analysis summary:**
```
Total Revenue    :  $68,600,278.74
Total Orders     :           5,000
Active Suppliers :              50
Products at Risk :              20
Avg Delay (days) :            6.65
```

---

## 🌐 JS Data Generator (Collaborator Tool)

A browser-based data generation interface built with **Node.js + Express + MySQL2** for collaborators who prefer JavaScript.

Features:
- Terminal-style live UI with real-time progress tracking
- Configurable DB connection via browser form
- Streams insert progress via Server-Sent Events (SSE)
- Generates the same 9,450 rows as the Python version

**To run:**
```bash
cd js
npm install
node server.js
# Open http://localhost:3000
```

---

## 📊 Power BI Dashboard

Five interactive dashboard pages connected to `data/clean/` CSV files:

| Page | Visuals |
|---|---|
| Executive Summary | KPI cards — revenue, orders, on-time rate, stockouts |
| Revenue Trends | Line chart with forecast overlay, category donut |
| Supplier Scorecard | Performance tiers, country rankings, top/bottom 10 |
| Inventory Health | Stockout alerts table, warehouse value bars, reorder queue |
| Shipment Analysis | Carrier reliability, delay trends, cost-at-risk |

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Database | MySQL 8.0 |
| Data Generation | Python, Faker, mysql-connector |
| Analysis & Forecasting | Python, pandas, NumPy, scikit-learn |
| Visualization | matplotlib, seaborn |
| Dashboard | Power BI Desktop |
| Collaboration Tool | Node.js, Express, MySQL2 |
| Version Control | Git, GitHub |

---

## ⚙️ Setup & Installation

### Prerequisites
- MySQL 8.0+
- Python 3.10+
- Node.js 18+
- Power BI Desktop (free)

### 1. Clone the repo
```bash
git clone https://github.com/waren23greg-stack/supply-chain-intelligence.git
cd supply-chain-intelligence
```

### 2. Set up the database
```bash
mysql -u root -p < sql/01_create_schema.sql
```

### 3. Install Python dependencies
```bash
pip install pandas faker mysql-connector-python sqlalchemy matplotlib seaborn scikit-learn
```

### 4. Generate data
```bash
cd python
# Update DB_PASSWORD in 01_data_generator.py
python 01_data_generator.py
```

### 5. Run analysis
```bash
python 02_analysis.py
```

### 6. Run SQL analytics
```bash
mysql -u root -p supply_chain < sql/02_analytics_queries.sql
```

### 7. Open Power BI
Open `powerbi/supply_chain_dashboard.pbix` and refresh data sources.

---

## 📈 Key Business Insights

- **$68.6M** in total revenue analyzed across 24 months
- **25% cancellation rate** flagged for investigation
- **20 products** identified as needing immediate reorder ($194K reorder cost)
- **DB Schenker** ranked #1 carrier with 36.2% on-time rate
- **UK suppliers** lead on-time performance at 35.5%
- Revenue trend is **stable with slight growth** — forecast projects ~$2.2M/month

---

## 👨‍💻 Author

**Waren Greg**
Statistics & IT Student | Aspiring Data Analyst

[![GitHub](https://img.shields.io/badge/GitHub-waren23greg--stack-181717?style=flat&logo=github)](https://github.com/waren23greg-stack)

---

## 🤝 Open To

- 📌 Data Analytics Internships
- 🤝 Collaboration on analytics projects
- 💬 Connecting with professionals in Data, BI & Analytics

---

*Built as a portfolio project to demonstrate end-to-end data analytics skills using industry-standard tools.*
