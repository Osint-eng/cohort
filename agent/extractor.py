"""Cohort Task Extraction Agent (Gemini + mock).

Set key locally only:
  export GEMINI_API_KEY=...
  # or put in .env (gitignored)

Offline demo (no key needed):
  export COHORT_MOCK=1

Never commit the key.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

from .schemas import BoardProposal

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
MOCK = os.environ.get("COHORT_MOCK", "").strip().lower() in ("1", "true", "yes")
DEFAULT_MODEL = os.environ.get("COHORT_MODEL", "gemini-2.0-flash")

SYSTEM_PROMPT = """You are the extraction engine for Cohort, an AI workspace for student teams.
Turn messy project input into a clean task board.
Rules: structured work items only; verb-led titles; owners only if named in source;
due dates YYYY-MM-DD when clear; capture dependencies; open questions if unsure.
Respond with ONLY valid JSON (no markdown):
{
  "project_summary": "string",
  "tasks": [{
    "id": "t1", "title": "string", "description": "string",
    "suggested_owner": null, "due_date": null, "depends_on": [],
    "status": "todo", "priority": "medium"
  }],
  "open_questions": [],
  "suggested_next_actions": []
}
status: todo|in_progress|blocked|done  priority: low|medium|high
"""


def _mock_board(
    team_members: list[str] | None = None,
    project_deadline: str | None = None,
) -> BoardProposal:
    """Deterministic sample board for offline / demo use."""
    members = team_members or ["Sam", "Priya", "Alex"]
    deadline = project_deadline or "2025-10-15"
    data = {
        "project_summary": (
            "Student team building a study-group matcher web app "
            "(design doc, React UI, API + matching, demo, writeup)."
        ),
        "tasks": [
            {
                "id": "t1",
                "title": "Draft 4-page design document",
                "description": "Architecture, matching approach, and screen list.",
                "suggested_owner": members[0] if members else "Sam",
                "due_date": "2025-10-05",
                "depends_on": [],
                "status": "todo",
                "priority": "high",
            },
            {
                "id": "t2",
                "title": "Build React UI screens",
                "description": "Main flows for forming and joining study groups.",
                "suggested_owner": members[1] if len(members) > 1 else "Priya",
                "due_date": "2025-10-11",
                "depends_on": ["t1"],
                "status": "todo",
                "priority": "high",
            },
            {
                "id": "t3",
                "title": "Scaffold backend API + matching",
                "description": "Auth, simple matching by skills and availability.",
                "suggested_owner": members[2] if len(members) > 2 else "Alex",
                "due_date": "2025-10-11",
                "depends_on": ["t1"],
                "status": "todo",
                "priority": "high",
            },
            {
                "id": "t4",
                "title": "Record demo video",
                "description": "Short walkthrough of the working app.",
                "suggested_owner": None,
                "due_date": "2025-10-12",
                "depends_on": ["t2", "t3"],
                "status": "todo",
                "priority": "medium",
            },
            {
                "id": "t5",
                "title": "Write final reflection",
                "description": "Team writeup for submission.",
                "suggested_owner": members[0] if members else "Sam",
                "due_date": deadline,
                "depends_on": ["t4"],
                "status": "todo",
                "priority": "medium",
            },
        ],
        "open_questions": [
            "Where will the app be hosted?",
            "Is external auth (Google) required or is email enough?",
        ],
        "suggested_next_actions": [
            "Confirm owners on the board",
            "Sam starts design doc so API and UI can unblock",
            "Agree on demo time for Oct 12",
        ],
    }
    return BoardProposal.model_validate(data)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"No JSON found:\n{text[:500]}")
    return json.loads(text[start : end + 1])


def _get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Missing GEMINI_API_KEY.\n"
            "  export GEMINI_API_KEY=...   (from https://aistudio.google.com/app/apikey)\n"
            "  or offline: export COHORT_MOCK=1"
        )
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


def _chat_once(client: Any, model: str, user_content: str) -> str:
    response = client.models.generate_content(
        model=model,
        contents=user_content,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "temperature": 0.2,
            "max_output_tokens": 2048,
        },
    )
    return response.text or ""


def extract_board(
    source_text: str,
    *,
    team_members: list[str] | None = None,
    project_deadline: str | None = None,
    model: str | None = None,
    client: Any = None,
) -> BoardProposal:
    if MOCK:
        print("[COHORT_MOCK=1] Using offline sample board (no API call).")
        return _mock_board(team_members, project_deadline)

    client = client or _get_client()
    model = model or DEFAULT_MODEL

    ctx = []
    if team_members:
        ctx.append("Known team members: " + ", ".join(team_members))
    if project_deadline:
        ctx.append("Overall project deadline: " + project_deadline)
    user_content = (
        "\n".join(ctx)
        + "\n\n<source>\n"
        + source_text.strip()
        + "\n</source>\n\nExtract a task board. Reply with JSON only."
    )

    try:
        raw = _chat_once(client, model, user_content)
        return BoardProposal.model_validate(_extract_json(raw))
    except Exception as e:
        raise RuntimeError(
            f"Gemini extraction failed: {e}\n"
            "Fix options:\n"
            "  1) Offline demo:  export COHORT_MOCK=1\n"
            "  2) Check key:     export GEMINI_API_KEY=...\n"
            "  3) Try a model:   export COHORT_MODEL=gemini-2.0-flash\n"
            "  4) Key page:      https://aistudio.google.com/app/apikey"
        ) from e


def extract_board_as_dict(source_text: str, **kwargs: Any) -> dict[str, Any]:
    return extract_board(source_text, **kwargs).model_dump()
