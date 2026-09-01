# Cohort Agent

Structured extraction + selective board agent for student team projects.

## Setup (local only)

```bash
pip install openai pydantic python-dotenv

# Create .env (never commit this file)
echo 'OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY' > .env
```

Get a key at https://openrouter.ai/keys — do not put it in git.

## Run

```bash
# Offline demo (no key, no credits)
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py

# Live via OpenRouter
unset COHORT_MOCK
set -a; source .env; set +a
python examples/run_extraction.py
python examples/run_agent.py
```

Optional model override:

```bash
export COHORT_MODEL=openrouter/free
# or any free model slug from https://openrouter.ai/models
```

## Design

- **Extraction** forces structured JSON (owners, dates, deps) — not essays.
- **Board agent** only nags late/blocked work and writes a contribution log.
- Mock mode always available so demos never depend on credits.
