# Cohort

**Live AI agent that runs student group projects.**

Paste a brief or team chat. Cohort builds a task board, nags only what is late, and keeps a contribution log your professor can trust.

It does not write the homework. It runs the project.

---

## Live agent (browser)

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Offline demo (no API key)
export COHORT_MOCK=1
python app.py
```

Open **http://127.0.0.1:7860**

1. Paste a project brief or chat log → board appears  
2. Chat: `check-in` · `list tasks` · `mark t1 complete` · `mark t2 blocked because API down`  
3. Contribution log updates live  

### Live with Gemini

```bash
# .env (gitignored)
# GEMINI_API_KEY=your_key
set -a; source .env; set +a
unset COHORT_MOCK
python app.py
```

## Terminal live agent

```bash
export COHORT_MOCK=1
python examples/live_cli.py
```

Type `/paste`, paste a brief, empty line, then chat with the agent.

## One-shot demos

```bash
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py
```

## What the agent does

| Piece | Role |
|-------|------|
| Extraction agent | Messy input → structured tasks (owners, dates, dependencies) |
| Board agent | Check-ins, mark complete/blocked |
| Contribution log | Who did what — fair record for the team and professor |

## Project structure

```
cohort/
├── app.py                 # Live browser agent (Gradio)
├── agent/
│   ├── extractor.py       # Paste → board
│   ├── agent.py           # Board actions + log
│   └── schemas.py
├── examples/
│   ├── live_cli.py        # Terminal REPL
│   ├── run_extraction.py
│   └── run_agent.py
└── requirements.txt
```

## Design

- Agent, not chatbot essay writer
- Selective (only late / blocked)
- Structured output (Pydantic)
- Offline mock mode for demos
- Secrets stay in local `.env`

## License

MIT
