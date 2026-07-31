# 🌐 Supply Chain Intelligence Platform

An enterprise-grade, **agentic Supply Chain Intelligence Engine** designed to replace static dashboards with automated risk prediction, lead-time variance simulation, and proactive inventory mitigation.

## 🏗️ Architecture Overview

The system uses a state-based multi-agent architecture:
1. **Market Signal Agent:** Continuously scores suppliers on historical OTIF (On-Time In-Full) and geopolitical risk indexes.
2. **Logistics Agent:** Computes dynamic lead-time inflation based on transit corridor friction.
3. **Inventory Strategist Agent:** Reconciles SKU burn rates against effective lead times to predict stockout dates and recommend specific executive interventions (e.g., Air Freight Expedite).

## 🚀 Quick Reference

### Directory Structure
├── intelligence_engine/
│   ├── config.py         # App configuration & thresholds
│   ├── schemas.py        # Pydantic domain models & shared state
│   └── agents.py         # Multi-agent LangGraph workflow engine
├── backend/
│   └── main.py           # FastAPI service API
└── requirements.txt      # Project dependencies


### Running Locally
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
API Documentation: Visit http://localhost:8000/docs

Demo Scenario: Visit http://localhost:8000/api/v1/demo-scenario


---

## Next Steps for You:
1. Open your GitHub repository in your browser.
2. For each file above, click **Add file** -> **Create new file**.
3. Type the exact path (e.g., `intelligence_engine/schemas.py`), paste the code block, and click **Commit changes**.

<ElicitationsGroup message="What should we add to the repository next?">
  <Elicitation label="Build the Supplier Risk Scorecard Frontend" query="Generate a modern, responsive single-page React (Next.js/Tailwind) UI component that displays the supplier risk scorecard and calls our `/api/v1/demo-scenario` endpoint."/>
  <Elicitation label="Add a What-If Monte Carlo Simulator" query="Create a new Python file `intelligence_engine/simulations.py` that runs 1,000 Monte Carlo simulations on supplier lead times to generate a stock-out probability curve."/>
  <Elicitation label="Create a GitHub Actions CI/CD Workflow" query="Write a `.github/workflows/ci.yml` file to automatically test our multi-agent pipeline and validate code syntax whenever we commit to GitHub."/>
</ElicitationsGroup>
