---
title: Cohort
emoji: 🧩
colorFrom: orange
colorTo: yellow
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
---

# Cohort

**Group chat agent for student teams.**

Create a room, invite teammates, chat together. Mention `@cohort` to extract a task board, run check-ins, mark work complete, and keep a shared contribution log.

It does not write the homework. It runs the project for the whole group.

---

## Live demo

After deploy: `https://huggingface.co/spaces/Osint-eng/cohort`

## Quick start (local)

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

1. Enter your **name** → **Create / Join room**
2. Share the room code
3. In chat: `@cohort sample` · `@cohort check-in` · `@cohort mark t1 complete`

## Deploy to Hugging Face Spaces (public URL)

```bash
cd cohort
source venv/bin/activate
pip install -U gradio huggingface_hub

# Login once (browser or token)
huggingface-cli login

# Deploy
gradio deploy
```

Or create a Space at https://huggingface.co/new-space  
- SDK: **Gradio** · Space name: `cohort` · link this GitHub repo

Set Space secret if needed: `COHORT_MOCK=1` (already the default).

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

## License

MIT
