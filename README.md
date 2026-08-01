# 🌐 Supply Chain Intelligence Platform

> **An agentic, enterprise-grade supply chain analytics engine** that replaces static dashboards with automated risk prediction, lead-time variance simulation, and proactive inventory mitigation.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-multi--agent-purple)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](Dockerfile)

---

## ✨ What It Does

Most supply chain tools tell you what *happened*. This platform tells you what's *about to happen* — and what to do about it.

Three specialized AI agents collaborate in a state-based pipeline to:

| Agent | Role |
|---|---|
| **Market Signal Agent** | Scores suppliers on OTIF (On-Time In-Full) history and geopolitical risk indexes |
| **Logistics Agent** | Computes dynamic lead-time inflation from transit corridor friction data |
| **Inventory Strategist Agent** | Reconciles SKU burn rates against effective lead times, predicts stockout dates, and recommends executive interventions (e.g. Air Freight Expedite) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│              (POST /api/v1/analyze)                      │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   LangGraph Engine  │
              │  (Multi-Agent DAG)  │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
  Market Signal     Logistics      Inventory
     Agent           Agent        Strategist
  (Supplier Risk) (Lead Times)  (Recommendations)
```

**Stack:** FastAPI · LangGraph · OpenAI · Pydantic v2 · SQLAlchemy · PostgreSQL · scikit-learn · pandas · Docker

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (or use Docker Compose to spin one up)
- An OpenAI API key

### 1. Clone & install

```bash
git clone https://github.com/gregewarengmaicom/supply-chain-intelligence.git
cd supply-chain-intelligence
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values:
# OPENAI_API_KEY=sk-...
# DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain
```

### 3. Run with Docker (recommended)

```bash
docker-compose up --build
```

### 4. Run locally

```bash
uvicorn backend.main:app --reload --port 8000
```

**API docs:** http://localhost:8000/docs

**Live demo scenario:** http://localhost:8000/api/v1/demo-scenario

---

## 📁 Project Structure

```
supply-chain-intelligence/
├── intelligence_engine/
│   ├── agents.py          # LangGraph multi-agent workflow
│   ├── schemas.py         # Pydantic domain models & shared state
│   └── config.py          # Thresholds & configuration
├── backend/
│   └── main.py            # FastAPI service
├── data_pipeline/         # ETL scripts
├── data/clean/            # Cleaned sample datasets
├── sql/                   # Analytics queries
├── python/                # Standalone analysis scripts
├── js/                    # Frontend utilities
├── frontend/              # UI components
├── tests/                 # Test suite
├── docs/charts/           # Exported visualizations
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔌 API Reference

### `GET /api/v1/demo-scenario`
Runs the full multi-agent pipeline on a pre-loaded demo dataset. Returns supplier risk scores, lead-time forecasts, and inventory recommendations.

### `POST /api/v1/analyze`
Accepts a JSON payload with your own supplier and inventory data and returns a full intelligence report.

See `/docs` for full interactive API documentation.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first, then:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/monte-carlo-sim`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

## 🙋 Author

Built by [@gregewarengmaicom](https://github.com/gregewarengmaicom).
