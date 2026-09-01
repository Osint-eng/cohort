# Cohort

**AI agent that runs student group projects.**

Paste a brief, chat export, or meeting notes. Cohort extracts tasks, assigns owners, sets due dates, nags only what is late or blocked, and keeps a contribution log your team (and your professor) can trust.

It does not write the assignment. It runs the project.

---

## The problem

Every group project starts the same way:

- A WhatsApp or Discord dump
- A half-empty Google Doc
- Three people who each think someone else owns the slides

By week three the work is uneven, the deadline is close, and nobody can show the professor who actually did what. The person who always herds the group burns out.

Students do not need another chatbot. They need an **agent** that turns chaos into owners, deadlines, and a fair record.

## What Cohort is

Cohort is a complete AI agent for student teams. Not a SaaS shell. Not a prompt demo.

```
Brief / chat / notes
        ↓
  Extraction agent
  (structured task board)
        ↓
  Board agent
  (check-ins, mark done/blocked)
        ↓
  Contribution log
  (who did what)
```

### Capabilities

| Capability | What it does |
|------------|--------------|
| **Extraction agent** | Turns messy input into structured tasks with owners, due dates, dependencies |
| **Board agent** | Selective check-ins — only late or blocked items |
| **Actions** | Mark complete, mark blocked, list tasks |
| **Contribution log** | Records who completed / blocked / unblocked work |
| **Mock mode** | Full offline demo with no API key |

## Quick start

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Offline demo (no key needed)
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py

# Live Gemini
# Put GEMINI_API_KEY=... in a local .env (never commit it)
set -a; source .env; set +a
unset COHORT_MOCK
python examples/run_extraction.py
python examples/run_agent.py
```

Get a free Gemini key at [Google AI Studio](https://aistudio.google.com/app/apikey).

## Project structure

```
cohort/
├── agent/                 # The complete agent
│   ├── schemas.py         # Task, BoardProposal, ContributionEvent
│   ├── extractor.py       # Paste → structured board (Gemini or mock)
│   ├── agent.py           # Board agent: check-in, complete, blocked, log
│   └── README.md
├── examples/
│   ├── run_extraction.py  # Demo: extraction agent
│   └── run_agent.py       # Demo: full loop
├── docs/
│   ├── presentation.html
│   └── SUBMISSION.md
├── requirements.txt
└── README.md
```

## How the agent works

### 1. Extraction agent
Input: assignment brief + team chat.  
Output: validated JSON board (tasks, owners, dates, dependencies, open questions).

Uses Gemini with forced JSON mode. Falls back to a deterministic mock board when `COHORT_MOCK=1`.

### 2. Board agent
Operates on the board:
- Drafts check-in messages for late/blocked/open items only
- Marks tasks complete or blocked
- Writes every action into a contribution log

### 3. Contribution log
Attributable events: who completed what, who marked something blocked.  
This is the fair record the professor can actually use.

## Design principles

1. **Agent, not chatbot** — structured work items, not essays
2. **Selective** — only intervenes when something is late or blocked
3. **Human in the loop** — proposes; people confirm
4. **Trustworthy log** — every meaningful action is attributable
5. **Runnable offline** — mock mode for demos and judges with no API key

## Tech

| Piece | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Schemas | Pydantic |
| Model | Gemini (`google-genai`) |
| Offline | `COHORT_MOCK=1` |
| Secrets | Local `.env` only (gitignored) |

## License

MIT

---

Built for people who have been the herder one too many times.
