#!/usr/bin/env python3
"""Cohort Live Agent — interactive chat UI (Gradio 6).

  export COHORT_MOCK=1
  python app.py
  open http://127.0.0.1:7860
"""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from agent import BoardStore, extract_board, run_agent

store: BoardStore | None = None


def board_summary() -> str:
    if not store or not store.board:
        return "_No board yet. Paste a project brief or chat log to start._"
    lines = [f"**Project:** {store.board.project_summary}\n"]
    for t in store.board.tasks:
        owner = t.suggested_owner or "unassigned"
        due = t.due_date or "no date"
        status = t.status.value if hasattr(t.status, "value") else str(t.status)
        lines.append(f"- `{t.id}` **{t.title}** — @{owner} — {status} — due {due}")
    if store.contribution_log:
        lines.append("\n**Contribution log**")
        for e in store.contribution_log:
            lines.append(f"- {e.actor} {e.action} `{e.task_id}`")
    return "\n".join(lines)


def looks_like_brief(text: str) -> bool:
    if len(text) > 280:
        return True
    keys = ("due", "deliverable", "assignment", "team", "project", "deadline", "chat:")
    return sum(1 for k in keys if k in text.lower()) >= 2


def respond(message: str, history: list):
    """Gradio 6 messages format: history is list[{role, content}]."""
    global store
    message = (message or "").strip()
    history = list(history or [])

    if not message:
        return "", history

    # Build or rebuild board from a pasted brief
    if store is None or looks_like_brief(message):
        try:
            board = extract_board(
                message,
                team_members=["Sam", "Priya", "Alex"],
            )
            store = BoardStore(board)
            reply = (
                "Board created from your input.\n\n"
                + board_summary()
                + "\n\nTry: **check-in**, **list tasks**, **mark t1 complete**, "
                "**mark t2 blocked because API down**"
            )
        except Exception as e:
            reply = (
                f"Could not extract a board: {e}\n\n"
                "Tip: export COHORT_MOCK=1 or set GEMINI_API_KEY in .env"
            )
    else:
        try:
            reply = run_agent(message, store)
            if store.board:
                reply = reply + "\n\n---\n" + board_summary()
        except Exception as e:
            reply = f"Agent error: {e}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return "", history


def reset():
    global store
    store = None
    return "", []


def main():
    import gradio as gr

    with gr.Blocks(title="Cohort — Live Agent") as demo:
        gr.Markdown(
            """
# Cohort — Live Agent
AI agent for student group projects.

1. Paste a project brief or team chat → board is created  
2. Then chat: `check-in` · `list tasks` · `mark t1 complete` · `mark t2 blocked because …`  
3. Contribution log updates as work is completed  

Offline: `export COHORT_MOCK=1` · Live: `GEMINI_API_KEY` in `.env`
            """
        )
        chatbot = gr.Chatbot(height=480, label="Cohort agent", type="messages")
        msg = gr.Textbox(
            placeholder="Paste a brief / chat log, or type: check-in · list tasks · mark t1 complete",
            label="Message",
            lines=3,
        )
        with gr.Row():
            send = gr.Button("Send", variant="primary")
            clear = gr.Button("Reset board")

        send.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
        clear.click(reset, outputs=[msg, chatbot])

    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
