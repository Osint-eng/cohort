"""Cohort Board Agent (Gemini + mock).

Set key locally: export GEMINI_API_KEY=...
Offline: export COHORT_MOCK=1
Never commit the key.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timezone
from typing import Any

from dotenv import load_dotenv

from .schemas import BoardProposal, ContributionEvent, Task, TaskStatus

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
DEFAULT_MODEL = os.environ.get("COHORT_MODEL", "gemini-3.6-flash")
MOCK = os.environ.get("COHORT_MOCK", "").strip().lower() in ("1", "true", "yes")


class BoardStore:
    def __init__(self, board: BoardProposal | None = None):
        self.board = board
        self.contribution_log: list[ContributionEvent] = []

    def list_tasks(self) -> list[dict[str, Any]]:
        if not self.board:
            return []
        return [t.model_dump(mode="json") for t in self.board.tasks]

    def get_task(self, task_id: str) -> Task | None:
        if not self.board:
            return None
        for t in self.board.tasks:
            if t.id == task_id:
                return t
        return None

    def update_task(self, task_id: str, **fields: Any) -> Task | None:
        task = self.get_task(task_id)
        if not task:
            return None
        data = task.model_dump(mode="json")
        data.update(fields)
        updated = Task.model_validate(data)
        assert self.board is not None
        self.board.tasks = [
            updated if t.id == task_id else t for t in self.board.tasks
        ]
        return updated

    def log(self, event: ContributionEvent) -> None:
        if event.timestamp is None:
            event.timestamp = datetime.now(timezone.utc).isoformat()
        self.contribution_log.append(event)


def _client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. "
            "export GEMINI_API_KEY=... or COHORT_MOCK=1"
        )
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


def _chat(client: Any, system: str, user: str, model: str) -> str:
    try:
        response = client.models.generate_content(
            model=model,
            contents=user,
            config={
                "system_instruction": system,
                "temperature": 0.3,
                "max_output_tokens": 1024,
            },
        )
        return response.text or ""
    except Exception as e:
        return f"(model unavailable: {e})"


def draft_checkin_message(store: BoardStore) -> str:
    today = date.today().isoformat()
    late_or_blocked = []
    for t in store.list_tasks():
        status, due = t.get("status"), t.get("due_date")
        if status == "blocked" or (due and due < today and status != "done"):
            late_or_blocked.append(t)
    if not late_or_blocked:
        open_tasks = [t for t in store.list_tasks() if t.get("status") != "done"]
        if not open_tasks:
            return "All clear — nothing is late or blocked right now."
        lines = ["Quick check-in — items needing attention:\n"]
        for t in open_tasks:
            owner = t.get("suggested_owner") or "unassigned"
            lines.append(
                f"[{t['id']}] {t['title']} (@{owner}) — {t.get('status')}, due {t.get('due_date') or 'no date'}"
            )
        lines.append("\nReply with status or blockers. Thanks!")
        return "\n".join(lines)

    lines = ["Quick check-in — items needing attention:\n"]
    for t in late_or_blocked:
        owner = t.get("suggested_owner") or "unassigned"
        lines.append(
            f"[{t['id']}] {t['title']} (@{owner}) — {t.get('status')}, due {t.get('due_date') or 'no date'}"
        )
    lines.append("\nReply with status or blockers. Thanks!")
    return "\n".join(lines)


def _extract_task_id(msg: str) -> str | None:
    m = re.search(r"\btask\s+(t\d+)\b", msg)
    if m:
        return m.group(1)
    m = re.search(r"\b(t\d+)\b", msg)
    if m:
        return m.group(1)
    return None


def run_agent(
    user_message: str,
    store: BoardStore,
    *,
    model: str | None = None,
    client: Any = None,
) -> str:
    model = model or DEFAULT_MODEL
    msg = user_message.strip().lower()

    if any(
        k in msg
        for k in ("check-in", "checkin", "nag", "status update", "what's late")
    ):
        return draft_checkin_message(store)

    if "list" in msg and "task" in msg:
        tasks = store.list_tasks()
        if not tasks:
            return "Board is empty."
        return "Current board:\n" + "\n".join(
            f"[{t['id']}] {t['title']} — {t.get('status')} (@{t.get('suggested_owner') or 'unassigned'})"
            for t in tasks
        )

    if any(k in msg for k in ("complete", "done", "finished")):
        tid = _extract_task_id(msg)
        if not tid:
            return "Could not find a task id (e.g. t1). Try: Mark task t1 complete."
        actor_m = re.search(r"\b([A-Z][a-z]+)\b", user_message)
        actor = actor_m.group(1) if actor_m else "someone"
        task = store.update_task(tid, status=TaskStatus.DONE)
        if not task:
            return f"Task {tid} not found."
        store.log(ContributionEvent(actor=actor, action="completed", task_id=tid))
        return f"Marked {tid} ({task.title}) as done. Logged contribution by {actor}."

    if "blocked" in msg:
        tid = _extract_task_id(msg)
        if not tid:
            return (
                "Could not find a task id (e.g. t1). "
                "Try: Mark task t2 blocked because API down."
            )
        reason_m = re.search(r"blocked(?:\s+because\s+(.+))?", msg)
        reason = (
            reason_m.group(1) if reason_m and reason_m.group(1) else "unspecified"
        ).strip()
        actor_m = re.search(r"\b([A-Z][a-z]+)\b", user_message)
        actor = actor_m.group(1) if actor_m else "someone"
        task = store.update_task(tid, status=TaskStatus.BLOCKED)
        if not task:
            return f"Task {tid} not found."
        store.log(
            ContributionEvent(actor=actor, action="blocked", task_id=tid, note=reason)
        )
        return f"Marked {tid} as blocked ({reason}). Logged by {actor}."

    if MOCK:
        return (
            "(Mock mode) I only handle check-in, list tasks, mark complete, "
            "and mark blocked offline. Unset COHORT_MOCK to use the live model."
        )

    client = client or _client()
    board_snapshot = json.dumps(store.list_tasks(), indent=2)
    system = (
        "You are the Cohort board agent for a student team. "
        "Be concise. Only discuss the existing board. Do not invent tasks."
    )
    user = (
        f"Current board:\n{board_snapshot}\n\n"
        f"User message: {user_message}\n\nReply helpfully."
    )
    return _chat(client, system, user, model)
