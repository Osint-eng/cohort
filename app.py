#!/usr/bin/env python3
"""Cohort Live Agent — interactive chat UI.

Run:
  export COHORT_MOCK=1          # offline
  # or set GEMINI_API_KEY in .env for live
  python app.py

Then open http://127.0.0.1:7860
"""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from agent import BoardStore, extract_board, run_agent
from agent.schemas import TaskStatus

# ---------------------------------------------------------------------------
# Session state (single-user demo)
# ---------------------------------------------------------------------------
store: BoardStore | None = None


def _board_summary() -> str:
    if not store or not store.board:
        return "_No board yet. Paste a project brief or chat log to start._"
    lines = [f"**Project:** {store.board.project_summary}\n"]
    for t in store.board.tasks:
        owner = t.suggested_owner or "unassigned"
        due = t.due_date or "no date"
        status = t.status.value if hasattr(t.status, "value") else t.status
        lines.append(f"- `{t.id}` **{t.title}** — @{owner} — {status} — due {due}")
    if store.contribution_log:
        lines.append("\n**Contribution log**")
        for e in store.contribution_log:
            lines.append(f"- {e.actor} {e.action} `{e.task_id}`")
    return "\n".join(lines)


def _is_brief(text: str) -> bool:
    """Heuristic: long text or looks like a project dump."""
    if len(text) > 280:
        return True
    keys = ("due", "deliverable", "assignment", "team", "project", "deadline", "chat:")
    return sum(1 for k in keys if k in text.lower()) >= 2


def chat(message: str, history: list) -> tuple[str, list]:
    global store
    message = (message or "").strip()
    if not message:
        return "", history

    # New board from pasted brief
    if store is None or _is_brief(message):
        try:
            board = extract_board(
                message,
                team_members=["Sam", "Priya", "Alex"],
            )
            store = BoardStore(board)
            reply = (
                "Board created from your input.\n\n"
                + _board_summary()
                + "\n\nTry: **check-in**, **list tasks**, **mark t1 complete**, **mark t2 blocked because API down**"
            )
        except Exception as e:
            reply = (
                f"Could not extract a board: {e}\n\n"
                "Tip: `export COHORT_MOCK=1` for offline mode, or check GEMINI_API_KEY."
            )
        history = history + [[message, reply]]
        return "", history

    # Operate on existing board
    try:
        reply = run_agent(message, store)
        # Always append current board snapshot for clarity
        if store.board:
            reply = reply + "\n\n---\n" + _board_summary()
    except Exception as e:
        reply = f"Agent error: {e}"

    history = history + [[message, reply]]
    return "", history


def reset() -> tuple[str, list]:
    global store
    store = None
    return "", []


def build_ui():
    import gradio as gr

    with gr.Blocks(title="Cohort — Live Agent") as demo:
        gr.Markdown(
            """
# Cohort — Live Agent
AI agent for student group projects.

**How to use**
1. Paste a project brief or team chat → agent builds the task board
2. Chat: `check-in`, `list tasks`, `mark t1 complete`, `mark t2 blocked because …`
3. Contribution log updates as work is completed

Offline: `export COHORT_MOCK=1`  ·  Live: set `GEMINI_API_KEY` in `.env`
            """
        )
        chatbot = gr.Chatbot(height=480, label="Cohort agent")
        msg = gr.Textbox(
            placeholder="Paste a brief / chat log, or type: check-in · list tasks · mark t1 complete",
            label="Message",
            lines=3,
        )
        with gr.Row():
            send = gr.Button("Send", variant="primary")
            clear = gr.Button("Reset board")

        send.click(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
        clear.click(reset, outputs=[msg, chatbot])

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)
