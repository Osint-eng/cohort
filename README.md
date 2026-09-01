# Cohort

**Group chat agent for student teams.**

Create a room, invite teammates, chat together. Mention `@cohort` to extract a task board, run check-ins, mark work complete, and keep a shared contribution log.

It does not write the homework. It runs the project for the whole group.

---

## Quick start

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export COHORT_MOCK=1
python app.py
```

Open **http://127.0.0.1:7860**

1. Enter your **name** (and optional project title)
2. Click **Create / Join room** — share the room code with teammates
3. Chat normally
4. Mention the agent:

```
@cohort sample
@cohort check-in
@cohort mark t1 complete
@cohort mark t2 blocked because API down
@cohort help
```

Everyone in the room shares the same board and contribution log.

### Live Gemini

```bash
# .env (gitignored): GEMINI_API_KEY=...
set -a; source .env; set +a
unset COHORT_MOCK
python app.py
```

## How it works

```
Group chat (shared room)
        ↓
  @cohort extract / sample
        ↓
  Shared task board
        ↓
  @cohort check-in / mark complete / blocked
        ↓
  Contribution log (fair record)
```

## Agent commands

| Command | Effect |
|---------|--------|
| `@cohort help` | List commands |
| `@cohort sample` | Load demo board |
| `@cohort extract` + brief | Build board from paste |
| `@cohort check-in` | What needs attention |
| `@cohort list` | Show tasks |
| `@cohort mark t1 complete` | Log completion |
| `@cohort mark t2 blocked because …` | Log blocker |

## Project structure

```
cohort/
├── app.py              # Group chat + agent UI
├── agent/
│   ├── extractor.py    # Brief → structured board
│   ├── agent.py        # Check-in, complete, blocked, log
│   └── schemas.py
├── examples/
└── requirements.txt
```

## Design

- Group-first: one room, one shared board
- Agent is a teammate you @mention — not a separate app
- Structured tasks + contribution log
- Works offline with `COHORT_MOCK=1`

## License

MIT
