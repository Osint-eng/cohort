# Cohort — Submission Package
AI Builders Hackathon

---

## A. Project Title & Descriptions

### Title
**Cohort**

### One-liner
AI agent for student teams that turns briefs, chats, and notes into owned tasks, deadlines, and a fair contribution log.

### Short description
Group projects start as chaos: WhatsApp dumps, half-empty docs, nobody owning the work. Cohort is not a homework writer. Paste a brief or chat log — the agent proposes a task board with owners and due dates, nags only what is late, and records who actually did what.

### Long description
Every group project starts the same way: a WhatsApp dump, a half-empty Google Doc, and three people who each think someone else owns the slides. By week three the work is uneven and nobody can show the professor who contributed.

Cohort is a complete AI agent for student teams. You paste a brief, syllabus excerpt, chat export, or meeting notes. The extraction agent turns that mess into a structured task board: titles, owners, due dates, dependencies. The board agent then runs the project — selective check-ins for late or blocked work, mark complete / blocked, and a contribution log that records who did what.

It does not write the assignment. It runs the project.

This is not a SaaS landing page or a thin wrapper. It is a runnable agent with structured schemas, forced JSON extraction, a selective board loop, and an offline mock mode so anyone can demo it without an API key.

**Who it is for**
- Student teams on group assignments, labs, hackathons, and club work
- The person who always ends up herding everyone else
- Professors who want a clean contribution trail

---

## Demo Video Script (≈ 4 minutes)

**Target:** 3:30–4:30  
**Tone:** Direct, student-to-student. Show the agent working.

### 0:00 – 0:40 | Problem
VO:  
“Every group project starts the same way. A WhatsApp dump, a half-empty Google Doc, and three people who each think someone else owns the slides. By week three nobody can show the professor who actually did what. Students don’t need another chatbot. They need an agent that turns chaos into owners, deadlines, and a fair record.”

### 0:40 – 1:20 | What Cohort is
VO:  
“Cohort is that agent. You paste a brief or chat log. It extracts a structured task board — titles, owners, due dates, dependencies. Then it runs the board: selective check-ins, mark complete, and a contribution log. It does not do the homework. It runs the project.”

### 1:20 – 2:30 | Live extraction
Show terminal. Run:
```bash
python examples/run_extraction.py
```
VO:  
“Here is the extraction agent on a real project brief. Five tasks, suggested owners, due dates, and dependencies. Structured work items — not an essay.”

### 2:30 – 3:40 | Board agent + log
Run:
```bash
python examples/run_agent.py
```
VO:  
“The board agent drafts a check-in for items that need attention, marks a task complete, and writes the contribution log. Sam completed t1. That is the fair record.”

### 3:40 – 4:10 | Close
VO:  
“AI only extracts structure and tracks ownership. The product is the agent workflow. Source code: github.com/Osint-eng/cohort.”

---

## Run commands (for judges / demo)

```bash
git clone https://github.com/Osint-eng/cohort.git
cd cohort
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Offline (no key)
export COHORT_MOCK=1
python examples/run_extraction.py
python examples/run_agent.py

# Live Gemini
# GEMINI_API_KEY in local .env
set -a; source .env; set +a
unset COHORT_MOCK
python examples/run_extraction.py
python examples/run_agent.py
```
