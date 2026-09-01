"""Cohort Board Agent (Hugging Face).

Set token locally: export HF_TOKEN=hf_...
Never commit the token.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timezone
from typing import Any

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from .schemas import BoardProposal, ContributionEvent, Task, TaskStatus

load_dotenv()

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
DEFAULT_MODEL = os.environ.get("COHORT_HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")


class BoardStore:
    def __init__(self, board: BoardProposal | None = None):
        self.board = board
        self.contribution_log: list[ContributionEvent] = []

    def list_tasks(self) -> list[dict[str, Any]]:
        if not self.board:
            return []
        return [t.model_dump() for t in self.board.tasks]

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
        data = task.model_dump()
        data.update(fields)
        updated = Task.model_validate(data)
        assert self.board is not None
        self.board.tasks = [updated if t.id == task_id else t for t in self.board.tasks]
        return updated

    def log(self, event: ContributionEvent) -> None:
        if event.timestamp is None:
            event.timestamp = datetime.now(timezone.utc).isoformat()
        self.contribution_log.append(event)


def _client() -> InferenceClient:
    if not HF_TOKEN:
        raise RuntimeError("Missing HF token. export HF_TOKEN=hf_...")
    return InferenceClient(token=HF_TOKEN)


def _chat(client: InferenceClient, system: str, user: str, model: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        return completion.choices[0].message.content or ""
    except Exception:
        prompt = system + "\n\nUser: " + user + "\n\nAssistant:"
        return client.text_generation(
            prompt, model=model, max_new_tokens=1024, temperature=0.3
        )


def draft_checkin_message(store: BoardStore) -> str:
    today = date.today().isoformat()
    late_or_blocked = []
    for t in store.list_tasks():
        status, due = t.get("status"), t.get("due_date")
        if status == "blocked" or (due and due < today and status != "done"):
            late_or_blocked.append(t)
    if not late_or_blocked:
        return "All clear — nothing is late or blocked right now."
    lines = ["Quick check-in — items needing attention:\n"]
    for t in late_or_blocked:
        owner = t.get("suggested_owner") or "unassigned"
        lines.append(
            f"- [{t['id']}] {t['title']} (@{owner}) — {t.get('status')}, due {t.get('due_date') or 'no date'}"
        )
    lines.append("\nReply with status or blockers. Thanks!")
    return "\n".join(lines)


def run_agent(
    user_message: str,
    store: BoardStore,
    *,
    model: str | None = None,
    client: InferenceClient | None = None,
) -> str:
    model = model or DEFAULT_MODEL
    msg = user_message.strip().lower()

    if any(k in msg for k in ("check-in", "checkin", "nag", "status update", "what's late")):
        return draft_checkin_message(store)

    if "list" in msg and "task" in msg:
        tasks = store.list_tasks()
        if not tasks:
            return "Board is empty."
        return "Current board:\n" + "\n".join(
            f"[{t['id']}] {t['title']} — {t.get('status')} (@{t.get('suggested_owner') or 'unassigned'})"
            for t in tasks
        )

    complete_match = re.search(
        r"(?:mark\s+)?(?:task\s+)?([a-z0-9_-]+)\s+(?:as\s+)?(?:complete|done|finished)", msg
    )
    if complete_match or ("finished" in msg and re.search(r"\b(t\d+)\b", msg)):
        tid = complete_match.group(1) if complete_match else re.search(r"\b(t\d+)\b", msg).group(1)
        actor_m = re.search(r"\b([A-Z][a-z]+)\b", user_message)
        actor = actor_m.group(1) if actor_m else "someone"
        task = store.update_task(tid, status=TaskStatus.DONE)
        if not task:
            return f"Task {tid} not found."
        store.log(ContributionEvent(actor=actor, action="completed", task_id=tid))
        return f"Marked {tid} ({task.title}) as done. Logged contribution by {actor}."

    blocked_match = re.search(
        r"(?:mark\s+)?(?:task\s+)?([a-z0-9_-]+)\s+(?:as\s+)?blocked(?:\s+because\s+(.+))?", msg
    )
    if blocked_match:
        tid = blocked_match.group(1)
        reason = (blocked_match.group(2) or "unspecified").strip()
        actor_m = re.search(r"\b([A-Z][a-z]+)\b", user_message)
        actor = actor_m.group(1) if actor_m else "someone"
        task = store.update_task(tid, status=TaskStatus.BLOCKED)
        if not task:
            return f"Task {tid} not found."
        store.log(ContributionEvent(actor=actor, action="blocked", task_id=tid, note=reason))
        return f"Marked {tid} as blocked ({reason}). Logged by {actor}."

    client = client or _client()
    board_snapshot = json.dumps(store.list_tasks(), indent=2)
    system = (
        "You are the Cohort board agent for a student team. "
        "Be concise. Only discuss the existing board. Do not invent tasks."
    )
    user = f"Current board:\n{board_snapshot}\n\nUser message: {user_message}\n\nReply helpfully."
    return _chat(client, system, user, model)
