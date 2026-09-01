"""
Cohort Board Agent
==================

A lightweight multi-turn agent that sits on top of an existing task board.

Capabilities (tools):
- list_tasks          — see current board state
- mark_blocked        — flag a task as blocked + reason
- mark_complete       — complete a task (records contribution)
- draft_checkin       — draft a selective nag / check-in message
- propose_reassignment — suggest a new owner

Pattern follows the classic tool-use agent loop from Anthropic cookbooks:
while stop_reason == "tool_use" → execute tools → feed results back.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from typing import Any, Callable

from anthropic import Anthropic
from dotenv import load_dotenv

from .schemas import BoardProposal, ContributionEvent, Task, TaskStatus

load_dotenv()

MODEL = os.environ.get("COHORT_MODEL", "claude-sonnet-4-5")


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
        self.board.tasks = [
            updated if t.id == task_id else t for t in self.board.tasks
        ]
        return updated

    def log(self, event: ContributionEvent) -> None:
        if event.timestamp is None:
            event.timestamp = datetime.now(timezone.utc).isoformat()
        self.contribution_log.append(event)


def make_tools(store: BoardStore):
    """Return (schemas, implementations) bound to this store."""

    def list_tasks() -> str:
        tasks = store.list_tasks()
        return json.dumps({"tasks": tasks, "count": len(tasks)}, indent=2)

    def mark_blocked(task_id: str, reason: str, actor: str) -> str:
        task = store.update_task(task_id, status=TaskStatus.BLOCKED)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        store.log(ContributionEvent(actor=actor, action="blocked", task_id=task_id, note=reason))
        return json.dumps({"ok": True, "task_id": task_id, "status": "blocked", "reason": reason})

    def mark_complete(task_id: str, actor: str, note: str = "") -> str:
        task = store.update_task(task_id, status=TaskStatus.DONE)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        store.log(ContributionEvent(actor=actor, action="completed", task_id=task_id, note=note or None))
        return json.dumps({"ok": True, "task_id": task_id, "status": "done"})

    def draft_checkin(focus: str = "late_or_blocked") -> str:
        today = date.today().isoformat()
        tasks = store.list_tasks()
        late_or_blocked = []
        for t in tasks:
            status = t.get("status")
            due = t.get("due_date")
            if status == "blocked":
                late_or_blocked.append(t)
            elif due and due < today and status != "done":
                late_or_blocked.append(t)
        if not late_or_blocked:
            return json.dumps({"message": "All clear — nothing is late or blocked right now.", "items": []})
        lines = ["Quick check-in — a few items need attention:\n"]
        for t in late_or_blocked:
            owner = t.get("suggested_owner") or "unassigned"
            status = t.get("status")
            due = t.get("due_date") or "no date"
            lines.append(f"- [{t['id']}] {t['title']} (@{owner}) — {status}, due {due}")
        lines.append("\nReply with status or blockers. Thanks!")
        return json.dumps({"message": "\n".join(lines), "items": late_or_blocked}, indent=2)

    def propose_reassignment(task_id: str, new_owner: str, reason: str, actor: str) -> str:
        task = store.update_task(task_id, suggested_owner=new_owner)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        store.log(ContributionEvent(actor=actor, action="reassigned", task_id=task_id, note=f"→ {new_owner}: {reason}"))
        return json.dumps({"ok": True, "task_id": task_id, "new_owner": new_owner, "reason": reason})

    implementations: dict[str, Callable[..., str]] = {
        "list_tasks": list_tasks,
        "mark_blocked": mark_blocked,
        "mark_complete": mark_complete,
        "draft_checkin": draft_checkin,
        "propose_reassignment": propose_reassignment,
    }

    schemas = [
        {"name": "list_tasks", "description": "List all tasks on the current board with status, owners, and due dates.", "input_schema": {"type": "object", "properties": {}, "required": []}},
        {"name": "mark_blocked", "description": "Mark a task as blocked and record who reported it.", "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}, "reason": {"type": "string"}, "actor": {"type": "string", "description": "Who is reporting the block"}}, "required": ["task_id", "reason", "actor"]}},
        {"name": "mark_complete", "description": "Mark a task as done and log the contribution.", "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}, "actor": {"type": "string"}, "note": {"type": "string"}}, "required": ["task_id", "actor"]}},
        {"name": "draft_checkin", "description": "Draft a short check-in / nag message that only mentions tasks that are late or blocked.", "input_schema": {"type": "object", "properties": {"focus": {"type": "string", "enum": ["late_or_blocked", "all_open"]}}, "required": []}},
        {"name": "propose_reassignment", "description": "Suggest a new owner for a task and log the change.", "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}, "new_owner": {"type": "string"}, "reason": {"type": "string"}, "actor": {"type": "string"}}, "required": ["task_id", "new_owner", "reason", "actor"]}},
    ]
    return schemas, implementations


SYSTEM = """You are the Cohort board agent for a student project team.

You help the team keep the board accurate and low-noise:
- Only surface what is late or blocked.
- Always log contribution events when status changes.
- Prefer short, clear messages the herder can paste into the group chat.
- Never invent tasks; only operate on the existing board via tools.

When the user asks for a status update or check-in, use draft_checkin.
When someone finishes work, use mark_complete.
When something is stuck, use mark_blocked.
"""


def run_agent(
    user_message: str,
    store: BoardStore,
    *,
    max_turns: int = 8,
    client: Anthropic | None = None,
) -> str:
    """Run a multi-turn tool-using agent against the board store."""
    client = client or Anthropic()
    schemas, implementations = make_tools(store)

    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM,
            tools=schemas,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            parts = [b.text for b in response.content if hasattr(b, "text") and b.type == "text"]
            return "\n".join(parts) if parts else "(no text response)"

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            fn = implementations.get(block.name)
            if not fn:
                result = json.dumps({"error": f"Unknown tool {block.name}"})
            else:
                try:
                    result = fn(**block.input)
                except Exception as e:
                    result = json.dumps({"error": str(e)})
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        messages.append({"role": "user", "content": tool_results})

    return "Agent stopped: max turns reached."
