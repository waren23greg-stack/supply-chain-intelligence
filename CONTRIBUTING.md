# Contributing to Supply Chain Intelligence

Thank you for your interest in contributing! This document covers everything you need to get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Conventions](#project-conventions)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Good First Issues](#good-first-issues)

---

## Code of Conduct

Be respectful, constructive, and kind. We're here to build something useful together.

---

## How to Contribute

There are several ways to help:

- **Bug reports** — Open an issue with steps to reproduce, expected vs actual behaviour, and your environment.
- **Feature requests** — Open an issue describing the use case and why it's valuable.
- **Code contributions** — Pick up an open issue, or propose something new via issue first.
- **Documentation** — Typos, clarity improvements, new examples — all welcome.
- **Sample data / test scenarios** — Real-world-shaped anonymised datasets make the demo more convincing.

---

## Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/supply-chain-intelligence.git
cd supply-chain-intelligence

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env — at minimum set OPENAI_API_KEY and DATABASE_URL

# 5. Start the API
uvicorn backend.main:app --reload --port 8000

# 6. Run the test suite
pytest tests/ -v
```

---

## Project Conventions

### Branching

| Branch | Purpose |
|---|---|
| `main` | Stable, always deployable |
| `dev` | Integration branch for active work |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Monte Carlo stockout simulator
fix: correct OTIF threshold comparison operator
docs: update setup instructions for Docker
test: add unit tests for Logistics Agent
```

### Code Style

- Python: formatted with [ruff](https://github.com/astral-sh/ruff) (`ruff check .`)
- Type hints required on all public functions
- Pydantic models for all data structures (see `intelligence_engine/schemas.py`)
- No bare `except:` clauses

### Adding a New Agent

1. Define its input/output state fields in `intelligence_engine/schemas.py`
2. Implement the agent function in `intelligence_engine/agents.py`
3. Wire it into the LangGraph DAG
4. Add at least one unit test in `tests/`
5. Document it in the README architecture section

---

## Submitting a Pull Request

1. Create a branch from `dev` (not `main`)
2. Make your changes, write tests, and ensure `pytest tests/ -v` passes
3. Push and open a PR against `dev`
4. Fill in the PR template — describe what changed and why
5. A maintainer will review within a few days

---

## Good First Issues

Look for issues labelled **`good first issue`** in the [Issues tab](https://github.com/gregewarengmaicom/supply-chain-intelligence/issues). Current candidates:

- Add a `/health` endpoint to the FastAPI backend
- Write unit tests for `schemas.py` validators
- Create a sample CSV seed dataset for the demo scenario
- Add a `Makefile` with common dev commands (`make run`, `make test`, `make lint`)
