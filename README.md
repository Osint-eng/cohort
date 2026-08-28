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

## Getting started

```bash
# Clone
git clone https://github.com/Osint-eng/cohort.git
cd cohort

# Install
pnpm install

# Environment
cp .env.example .env.local
# Fill in required keys

# Develop
pnpm dev
```

Open the local URL, create a project, and paste a sample brief to see the board generation flow.

## Project structure (high level)

```
/
├── apps/web          # TanStack Start + React frontend
├── packages/         # Shared types, UI, agent helpers
├── docs/             # Architecture notes
├── docs/presentation.html  # Pitch deck
└── README.md
```

## Design principles

1. **Human in the loop** — AI proposes; people decide.
2. **Structured output only** — tasks, owners, dates, dependencies. No free-form essays.
3. **Selective intervention** — the agent stays quiet unless something is late or blocked.
4. **Trustworthy log** — every meaningful action is recorded and attributable.
5. **Real multiplayer** — the board is the shared source of truth, not a private chat with a bot.

## Status

Draft / in-progress for the AI Builders Hackathon.

- Core loop and public demo: in progress
- Live URL, final repo structure, and architecture docs will be updated before the submission deadline

## License

MIT

---

Built for people who have been the herder one too many times.
