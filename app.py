#!/usr/bin/env python3
"""Cohort Live Agent — professional interactive UI.

  export COHORT_MOCK=1
  python app.py
  → http://127.0.0.1:7860
"""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from agent import BoardStore, extract_board, run_agent

store: BoardStore | None = None

SAMPLE_BRIEF = """CS 450 — Collaborative Study Group Matcher
Due: 15 October

Deliverables:
1. Design document (4 pages max)
2. Working web app (React + backend)
3. Demo video + final reflection

Team chat:
Sam: I'll own the design doc. Need it by Oct 5 so Alex can start the API.
Priya: Happy to take all the React UI.
Alex: Backend + matching once design is locked.
Sam: Also the final reflection writeup.
Priya: Demo video on the 12th."""


def board_markdown() -> str:
    if not store or not store.board:
        return (
            "### Board\n"
            "_Empty — paste a project brief in the chat to create a board._\n\n"
            "**Try the sample:** click **Load sample brief** below."
        )
    b = store.board
    lines = [
        "### Board",
        f"**{b.project_summary}**\n",
        "| ID | Task | Owner | Status | Due |",
        "|----|------|-------|--------|-----|",
    ]
    for t in b.tasks:
        owner = t.suggested_owner or "—"
        due = t.due_date or "—"
        status = t.status.value if hasattr(t.status, "value") else str(t.status)
        icon = {"todo": "○", "in_progress": "◐", "blocked": "⊘", "done": "●"}.get(
            status, "·"
        )
        lines.append(
            f"| `{t.id}` | {t.title} | @{owner} | {icon} {status} | {due} |"
        )

    if b.open_questions:
        lines.append("\n**Open questions**")
        for q in b.open_questions:
            lines.append(f"- {q}")

    if b.suggested_next_actions:
        lines.append("\n**Next actions**")
        for a in b.suggested_next_actions:
            lines.append(f"- {a}")

    if store.contribution_log:
        lines.append("\n### Contribution log")
        for e in store.contribution_log:
            note = f" — {e.note}" if e.note else ""
            lines.append(f"- **{e.actor}** {e.action} `{e.task_id}`{note}")

    return "\n".join(lines)


def looks_like_brief(text: str) -> bool:
    if len(text) > 280:
        return True
    keys = ("due", "deliverable", "assignment", "team", "project", "deadline", "chat:")
    return sum(1 for k in keys if k in text.lower()) >= 2


def respond(message: str, history: list):
    global store
    message = (message or "").strip()
    history = list(history or [])
    if not message:
        return "", history, board_markdown()

    if store is None or looks_like_brief(message):
        try:
            board = extract_board(
                message,
                team_members=["Sam", "Priya", "Alex"],
                project_deadline="2025-10-15",
            )
            store = BoardStore(board)
            reply = (
                "**Board created.** Review tasks on the right.\n\n"
                "Commands you can use:\n"
                "- `check-in` — what needs attention\n"
                "- `list tasks` — full board\n"
                "- `mark t1 complete` — log completion\n"
                "- `mark t2 blocked because …` — log blocker\n"
                "- `help` — show commands"
            )
        except Exception as e:
            reply = (
                f"Could not extract a board.\n\n`{e}`\n\n"
                "Use **Load sample brief** or `export COHORT_MOCK=1`."
            )
    else:
        low = message.lower().strip()
        if low in ("help", "commands", "?"):
            reply = (
                "**Commands**\n"
                "- `check-in` / `what's late`\n"
                "- `list tasks`\n"
                "- `mark t1 complete` (or t2, t3…)\n"
                "- `mark t2 blocked because <reason>`\n"
                "- Paste a new brief anytime to rebuild the board"
            )
        else:
            try:
                reply = run_agent(message, store)
            except Exception as e:
                reply = f"Agent error: `{e}`"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return "", history, board_markdown()


def load_sample(history: list):
    return respond(SAMPLE_BRIEF, history or [])


def reset():
    global store
    store = None
    return "", [], board_markdown()


CSS = """
.gradio-container {
  max-width: 1200px !important;
  font-family: system-ui, -apple-system, sans-serif !important;
}
footer { display: none !important; }
#board-panel {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  background: #fafafa;
  min-height: 420px;
}
"""


def main():
    import gradio as gr

    with gr.Blocks(title="Cohort — Live Agent") as demo:
        gr.Markdown(
            """
# Cohort
**Live AI agent for student group projects** — paste a brief, get a board, track who did what.
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=440, label="Agent")
                msg = gr.Textbox(
                    placeholder="Paste a project brief / chat log, or type a command…",
                    label="Message",
                    lines=3,
                )
                with gr.Row():
                    send = gr.Button("Send", variant="primary", scale=2)
                    sample = gr.Button("Load sample brief", scale=1)
                    clear = gr.Button("Reset", scale=1)

            with gr.Column(scale=2):
                board_view = gr.Markdown(
                    value=board_markdown(),
                    elem_id="board-panel",
                )
                gr.Markdown(
                    "**Quick commands**  \n"
                    "`check-in` · `list tasks` · `mark t1 complete` · "
                    "`mark t2 blocked because API down` · `help`"
                )

        gr.Markdown(
            "---\n"
            "Cohort does **not** write the assignment. It runs the project: owners, "
            "deadlines, and a fair contribution log.  \n"
            "Offline: `COHORT_MOCK=1` · Live Gemini: `GEMINI_API_KEY` in `.env` · "
            "[GitHub](https://github.com/Osint-eng/cohort)"
        )

        send.click(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot, board_view],
        )
        msg.submit(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot, board_view],
        )
        sample.click(
            load_sample,
            inputs=[chatbot],
            outputs=[msg, chatbot, board_view],
        )
        clear.click(reset, outputs=[msg, chatbot, board_view])

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
        theme=gr.themes.Soft(primary_hue="orange", neutral_hue="slate"),
    )


if __name__ == "__main__":
    main()
