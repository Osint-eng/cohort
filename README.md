# Cohort

**Live AI agent that runs student group projects.**

Paste a brief or team chat. Cohort builds a task board, nags only what is late, and keeps a contribution log your professor can trust.

It does not write the homework. It runs the project.

---

## Live agent (browser UI)

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export COHORT_MOCK=1          # offline demo, no API key
python app.py
```

Open **http://127.0.0.1:7860**

| Action | How |
|--------|-----|
| Create board | Paste a brief / chat, or click **Load sample brief** |
| Check-in | Type `check-in` |
| Complete work | `mark t1 complete` |
| Log blocker | `mark t2 blocked because API down` |
| Reset | **Reset** button |

### Live Gemini

```bash
# .env (never commit)
# GEMINI_API_KEY=your_key
set -a; source .env; set +a
unset COHORT_MOCK
python app.py
```

## What the agent does

```
Brief / chat
    → Extraction agent  (structured tasks, owners, dates)
    → Board agent       (check-ins, complete, blocked)
    → Contribution log  (who did what)
```

## Project structure

```
cohort/
├── app.py                 # Professional live UI
├── agent/
│   ├── extractor.py       # Paste → board
│   ├── agent.py           # Board actions + log
│   └── schemas.py
├── examples/
│   ├── live_cli.py
│   ├── run_extraction.py
│   └── run_agent.py
└── requirements.txt
```

## Design principles

1. Agent, not essay chatbot
2. Selective (only late / blocked)
3. Structured output (Pydantic)
4. Fair contribution log
5. Works offline (`COHORT_MOCK=1`)

## License

MIT
