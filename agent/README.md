# Cohort Agent

AI layer for Cohort: structured task extraction + selective board agent.

## Modes

| Mode | How |
|------|-----|
| Offline demo | `export COHORT_MOCK=1` |
| Live Gemini | `export GEMINI_API_KEY=...` (from [Google AI Studio](https://aistudio.google.com/app/apikey)) |

Never commit API keys. Put them only in a local `.env` (gitignored).

## Install

```bash
pip install google-genai pydantic python-dotenv
```

## Run

```bash
# Offline (recommended for demos)
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py

# Live Gemini
unset COHORT_MOCK
set -a; source .env; set +a   # .env contains GEMINI_API_KEY=...
python examples/run_extraction.py
python examples/run_agent.py
```

## Design

- **Extraction** forces structured JSON (owners, due dates, dependencies).
- **Board agent** only nags late/blocked items and writes a contribution log.
- The product is the workflow, not the model.
