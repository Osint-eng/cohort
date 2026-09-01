# Cohort Agent

Complete AI agent for student group projects.

## What it does

1. **Extraction agent** — messy brief/chat → structured task board (Pydantic-validated)
2. **Board agent** — selective check-ins, mark complete/blocked, contribution log
3. **Mock mode** — full offline demo with `COHORT_MOCK=1`

## Modes

| Mode | How |
|------|-----|
| Offline | `export COHORT_MOCK=1` |
| Live Gemini | `export GEMINI_API_KEY=...` (local `.env` only) |

Never commit API keys.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
# Offline
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py

# Live
unset COHORT_MOCK
set -a; source .env; set +a
python examples/run_extraction.py
python examples/run_agent.py
```

## Design

- Structured output only (tasks, owners, dates, dependencies)
- Selective intervention (late / blocked only)
- Contribution log for accountability
- Human stays in control
