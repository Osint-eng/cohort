#!/usr/bin/env python3
"""Cohort — Group chat agent for student teams.

  export COHORT_MOCK=1
  python app.py
  → http://127.0.0.1:7860

Create or join a room, chat with teammates, mention @cohort to run the agent.
"""

from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from agent import BoardStore, extract_board, run_agent

# ---------------------------------------------------------------------------
# In-memory rooms (demo scale)
# ---------------------------------------------------------------------------


@dataclass
class Room:
    code: str
    title: str = "Group project"
    messages: list[dict[str, Any]] = field(default_factory=list)
    store: BoardStore | None = None
    members: set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)


ROOMS: dict[str, Room] = {}
LOCK = Lock()


def _new_code() -> str:
    return secrets.token_hex(3).upper()  # e.g. A1B2C3


def get_or_create_room(code: str | None, title: str = "Group project") -> Room:
    with LOCK:
        if code:
            code = code.strip().upper()
            if code in ROOMS:
                return ROOMS[code]
        code = code.strip().upper() if code else _new_code()
        if code not in ROOMS:
            ROOMS[code] = Room(code=code, title=title or "Group project")
        return ROOMS[code]


def board_markdown(room: Room) -> str:
    if not room.store or not room.store.board:
        return (
            f"### Room `{room.code}`\n"
            f"_{room.title}_\n\n"
            "No board yet. In chat, type:\n"
            "`@cohort extract` then paste your brief,\n"
            "or `@cohort sample` for a demo board."
        )
    b = room.store.board
    lines = [
        f"### Room `{room.code}` — Board",
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
    if room.store.contribution_log:
        lines.append("\n### Contribution log")
        for e in room.store.contribution_log[-12:]:
            note = f" — {e.note}" if e.note else ""
            lines.append(f"- **{e.actor}** {e.action} `{e.task_id}`{note}")
    members = ", ".join(sorted(room.members)) or "—"
    lines.append(f"\n_Members: {members}_")
    return "\n".join(lines)


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


def agent_reply(room: Room, user: str, text: str) -> str:
    """Handle @cohort … commands."""
    body = text
    # strip mention
    body = re.sub(r"@cohort\b", "", body, flags=re.I).strip()
    low = body.lower()

    if low in ("help", "commands", "?", ""):
        return (
            f"Hey {user}. I run the project board for this room.\n\n"
            "**Commands**\n"
            "- `@cohort sample` — load demo board\n"
            "- `@cohort extract` + paste brief (next message or same line)\n"
            "- `@cohort check-in` — what needs attention\n"
            "- `@cohort list` — show tasks\n"
            "- `@cohort mark t1 complete` — log completion\n"
            "- `@cohort mark t2 blocked because …` — log blocker\n"
            "- `@cohort help`\n\n"
            "Everyone in the room shares the same board and contribution log."
        )

    if low.startswith("sample"):
        board = extract_board(
            SAMPLE_BRIEF,
            team_members=["Sam", "Priya", "Alex"],
            project_deadline="2025-10-15",
        )
        room.store = BoardStore(board)
        return f"Loaded sample board with **{len(board.tasks)} tasks**. See the panel →"

    if low.startswith("extract"):
        payload = body[7:].strip()  # after 'extract'
        if not payload:
            return (
                "Send the brief in the same message:\n"
                "`@cohort extract`\n"
                "<paste brief / chat log here>"
            )
        board = extract_board(
            payload,
            team_members=list(room.members) or ["Sam", "Priya", "Alex"],
        )
        room.store = BoardStore(board)
        return f"Board created — **{len(board.tasks)} tasks**. Everyone in `{room.code}` shares it."

    if room.store is None:
        return "No board yet. Use `@cohort sample` or `@cohort extract` with a brief."

    # Delegate to board agent (mark complete, check-in, list, blocked)
    return run_agent(body, room.store)


def post_message(
    room_code: str,
    display_name: str,
    message: str,
    history: list,
):
    name = (display_name or "Anon").strip()[:32] or "Anon"
    message = (message or "").strip()
    history = list(history or [])

    if not room_code or not room_code.strip():
        return "", history, "### Enter a room code and your name, then join."

    room = get_or_create_room(room_code)
    room.members.add(name)

    if not message:
        return "", history, board_markdown(room)

    # User message into history
    history.append({"role": "user", "content": f"**{name}:** {message}"})
    room.messages.append({"role": "user", "name": name, "text": message, "ts": time.time()})

    # Agent trigger
    if re.search(r"@cohort\b", message, flags=re.I) or message.lower().startswith("/"):
        try:
            # allow /check-in style
            text = message
            if text.startswith("/"):
                text = "@cohort " + text[1:]
            reply = agent_reply(room, name, text)
        except Exception as e:
            reply = f"Agent error: {e}"
        history.append({"role": "assistant", "content": f"**Cohort:** {reply}"})
        room.messages.append(
            {"role": "assistant", "name": "Cohort", "text": reply, "ts": time.time()}
        )

    return "", history, board_markdown(room)


def join_room(room_code: str, display_name: str, title: str):
    code = (room_code or "").strip().upper()
    name = (display_name or "Anon").strip()[:32] or "Anon"
    if not code:
        code = _new_code()
    room = get_or_create_room(code, title=title or "Group project")
    room.members.add(name)
    if title and title.strip():
        room.title = title.strip()
    hello = (
        f"Joined room **`{room.code}`** as **{name}**.\n\n"
        f"Share code **{room.code}** with teammates.\n"
        "Chat normally. Mention **@cohort** when you need the agent\n"
        "(e.g. `@cohort sample`, `@cohort check-in`, `@cohort mark t1 complete`)."
    )
    history = [{"role": "assistant", "content": f"**Cohort:** {hello}"}]
    return code, history, board_markdown(room)


def refresh_board(room_code: str):
    if not room_code or not room_code.strip():
        return "### Join a room first."
    room = get_or_create_room(room_code)
    return board_markdown(room)


CSS = """
.gradio-container { max-width: 1180px !important; }
footer { display: none !important; }
#board-panel {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  background: #fafafa;
  min-height: 460px;
}
"""


def main():
    import gradio as gr

    with gr.Blocks(title="Cohort — Group Agent") as demo:
        gr.Markdown(
            """
# Cohort
**Group chat agent for student teams** — share a room, chat, and let the agent run the project board.
            """
        )

        with gr.Row():
            room_in = gr.Textbox(
                label="Room code",
                placeholder="Leave empty to create · or paste a code to join",
                scale=2,
            )
            name_in = gr.Textbox(
                label="Your name",
                placeholder="e.g. Sam",
                scale=1,
            )
            title_in = gr.Textbox(
                label="Project title (optional)",
                placeholder="CS 450 matcher",
                scale=2,
            )
            join_btn = gr.Button("Create / Join room", variant="primary", scale=1)

        with gr.Row():
            with gr.Column(scale=3):
                chat = gr.Chatbot(label="Group chat", height=460)
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Chat with the group · @cohort help · @cohort sample · @cohort check-in",
                    lines=2,
                )
                with gr.Row():
                    send = gr.Button("Send", variant="primary")
                    refresh = gr.Button("Refresh board")

            with gr.Column(scale=2):
                board = gr.Markdown(
                    value="### Join or create a room to begin.",
                    elem_id="board-panel",
                )
                gr.Markdown(
                    """
**Agent commands** (type in chat)

`@cohort help`  
`@cohort sample`  
`@cohort extract` + brief  
`@cohort check-in`  
`@cohort list`  
`@cohort mark t1 complete`  
`@cohort mark t2 blocked because …`
                    """
                )

        gr.Markdown(
            "Cohort does **not** write the assignment — it runs the project for the whole group.  \n"
            "Offline: `COHORT_MOCK=1` · [GitHub](https://github.com/Osint-eng/cohort)"
        )

        # state of active room code for this browser session
        active_code = gr.State("")

        def do_join(code, name, title):
            new_code, history, md = join_room(code, name, title)
            return new_code, new_code, history, md

        def do_send(code, name, message, history):
            return post_message(code, name, message, history)

        join_btn.click(
            do_join,
            inputs=[room_in, name_in, title_in],
            outputs=[room_in, active_code, chat, board],
        )
        send.click(
            do_send,
            inputs=[active_code, name_in, msg, chat],
            outputs=[msg, chat, board],
        )
        msg.submit(
            do_send,
            inputs=[active_code, name_in, msg, chat],
            outputs=[msg, chat, board],
        )
        refresh.click(refresh_board, inputs=[active_code], outputs=[board])

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
        theme=gr.themes.Soft(primary_hue="orange", neutral_hue="slate"),
    )


if __name__ == "__main__":
    main()
