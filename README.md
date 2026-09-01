# Cohort

**AI workspace for student teams.**

Paste a brief, chat export, or meeting notes. Cohort extracts tasks, proposes owners and due dates, and keeps a contribution log your team (and your professor) can trust.

It does not write the assignment. It runs the project.

---

## The problem

Every group project starts the same way:

- A WhatsApp or Discord dump
- A half-empty Google Doc
- Three people who each think someone else owns the slides

By week three the work is uneven, the deadline is close, and nobody can show the professor who actually did what. The person who always herds the group burns out. Contribution becomes a he-said-she-said email thread.

Students do not need another chatbot. They need owners, deadlines, and a fair record.

## The solution

Cohort is a multi-player AI workspace built for student teams.

1. **Create a project** and invite teammates
2. **Drop in** a brief, syllabus excerpt, chat log, or notes
3. **Cohort proposes** a task board: titles, owners, due dates, dependencies
4. **You confirm or edit** — the board becomes the source of truth
5. **The agent** only nags what is late or blocked, and drafts the check-in message
6. **A contribution log** records who accepted, completed, and unblocked work

The result is a living board and an audit trail that survives the group chat.

## Who it is for

- Student teams on group assignments, labs, hackathons, and club work
- The person who always ends up herding everyone else
- Professors who want a clean contribution trail instead of a dispute

## Why this is not another AI demo

Most AI projects stop at a clever prompt or a single-player chat interface. Cohort is built as a small SaaS:

- Multi-player workspace with a live task board
- AI that produces **structured work items**, not essays
- Selective agent behavior (only late / blocked items)
- Persistent contribution log that can be shared
- Real authentication, data, and status views

The model is a tool. The product is the workflow.

## Tech stack

| Layer        | Choice                          |
|--------------|----------------------------------|
| Language     | TypeScript                      |
| Frontend     | React, TanStack Start, Tailwind |
| Hosting      | Vercel (PaaS)                   |
| Auth & Data  | Managed BaaS                    |
| Models       | API (structured extraction)     |
| Agent        | Claude tool-use (see `agent/`)  |

The product is the workflow, not the model.

## Core loop

```
Brief / chat / notes
        ↓
   Structured extraction
        ↓
  Proposed task board
        ↓
  Human confirm / edit
        ↓
   Live source of truth
        ↓
 Agent (late / blocked only)
        ↓
  Contribution log
```

## AI Agent (Claude)

The core intelligence lives in `agent/`, following Anthropic Claude Cookbook patterns (tool-use structured extraction + multi-turn agent loop).

```bash
pip install anthropic pydantic python-dotenv
export ANTHROPIC_API_KEY=sk-ant-...

python examples/run_extraction.py   # paste → board
python examples/run_agent.py        # selective nags + contribution log
```

See [`agent/README.md`](agent/README.md) for design principles and extension points.

## Getting started

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort

pip install anthropic pydantic python-dotenv
export ANTHROPIC_API_KEY=sk-ant-...
python examples/run_extraction.py
```

## Project structure

```
/
├── agent/                 # Claude extraction + board agent
│   ├── schemas.py
│   ├── extractor.py
│   ├── agent.py
│   └── README.md
├── examples/
│   ├── run_extraction.py
│   └── run_agent.py
├── docs/
│   ├── presentation.html  # Pitch deck
│   └── SUBMISSION.md
└── README.md
```

## Design principles

1. **Human in the loop** — AI proposes; people decide.
2. **Structured output only** — tasks, owners, dates, dependencies. No free-form essays.
3. **Selective intervention** — the agent stays quiet unless something is late or blocked.
4. **Trustworthy log** — every meaningful action is recorded and attributable.
5. **Real multiplayer** — the board is the shared source of truth, not a private chat with a bot.

## Status

In progress for the AI Builders Hackathon.

- Core agent loop: shipped (`agent/`)
- Public demo UI: in progress
- Live URL and full product code will land before the deadline

## License

MIT

---

Built for people who have been the herder one too many times.
