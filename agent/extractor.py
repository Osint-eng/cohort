"""
Cohort Task Extraction Agent
============================

Cookbook-style structured extraction using Claude tool use.
Pattern mirrors anthropic-cookbook/tool_use/extracting_structured_json.ipynb:
define a tool whose input_schema is the shape we want, force Claude to call it,
then read the structured input.

This is the core "paste → board" capability of Cohort.
"""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from .schemas import BoardProposal

load_dotenv()

MODEL = os.environ.get("COHORT_MODEL", "claude-sonnet-4-5")

# Tool definition — Claude is forced to produce this shape
EXTRACT_BOARD_TOOL: dict[str, Any] = {
    "name": "propose_task_board",
    "description": (
        "Propose a complete task board for a student group project. "
        "Call this tool with structured tasks extracted from the provided "
        "brief, chat log, or notes. Do not invent teammates who are not "
        "mentioned. Prefer concrete, actionable titles."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "project_summary": {
                "type": "string",
                "description": "One-paragraph summary of the project",
            },
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Short id e.g. t1, t2",
                        },
                        "title": {
                            "type": "string",
                            "description": "Action-oriented task title",
                        },
                        "description": {
                            "type": "string",
                            "description": "Context or acceptance criteria",
                        },
                        "suggested_owner": {
                            "type": ["string", "null"],
                            "description": "Name/handle if mentioned in the source",
                        },
                        "due_date": {
                            "type": ["string", "null"],
                            "description": "YYYY-MM-DD if a deadline is inferable",
                        },
                        "depends_on": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of task ids this depends on",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["todo", "in_progress", "blocked", "done"],
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                    },
                    "required": [
                        "id",
                        "title",
                        "description",
                        "depends_on",
                        "status",
                        "priority",
                    ],
                },
            },
            "open_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ambiguities the team should resolve",
            },
            "suggested_next_actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Immediate next steps",
            },
        },
        "required": [
            "project_summary",
            "tasks",
            "open_questions",
            "suggested_next_actions",
        ],
    },
}

SYSTEM_PROMPT = """You are the extraction engine for Cohort, an AI workspace for student teams.

Your job is to turn messy project input (assignment briefs, WhatsApp/Discord exports,
meeting notes, syllabus excerpts) into a clean, actionable task board.

Rules:
- Produce structured work items only. Never write the assignment itself.
- Prefer concrete, verb-led titles ("Draft literature review section", not "Literature").
- Only assign owners when a name or handle appears in the source text.
- Infer due dates only when the source gives clear timing relative to a known date or deadline.
- Capture dependencies when one task clearly blocks another.
- Surface open questions instead of guessing missing information.
- Keep the board small enough to be useful (typically 4–12 tasks).

Always call the propose_task_board tool with your final structured output.
"""


def extract_board(
    source_text: str,
    *,
    team_members: list[str] | None = None,
    project_deadline: str | None = None,
    client: Anthropic | None = None,
) -> BoardProposal:
    """
    Extract a proposed task board from free-text project material.

    Parameters
    ----------
    source_text:
        Brief, chat export, notes, or any mix of the above.
    team_members:
        Optional list of known teammate names/handles to bias owner suggestions.
    project_deadline:
        Optional overall deadline (YYYY-MM-DD) to help relative date inference.
    client:
        Optional Anthropic client (useful for testing).
    """
    client = client or Anthropic()

    context_bits = []
    if team_members:
        context_bits.append(f"Known team members: {', '.join(team_members)}")
    if project_deadline:
        context_bits.append(f"Overall project deadline: {project_deadline}")
    context = "\n".join(context_bits)

    user_content = f"""{context}

<source>
{source_text.strip()}
</source>

Extract a task board. Call the propose_task_board tool.
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[EXTRACT_BOARD_TOOL],
        tool_choice={"type": "tool", "name": "propose_task_board"},
        messages=[{"role": "user", "content": user_content}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "propose_task_board":
            return BoardProposal.model_validate(block.input)

    raise RuntimeError(
        "Claude did not call propose_task_board. "
        f"stop_reason={response.stop_reason}"
    )


def extract_board_as_dict(source_text: str, **kwargs: Any) -> dict[str, Any]:
    """Convenience wrapper that returns a plain dict (JSON-serializable)."""
    board = extract_board(source_text, **kwargs)
    return board.model_dump()


if __name__ == "__main__":
    # Quick smoke test — requires ANTHROPIC_API_KEY
    sample = """
    CS 450 Group Project — Due Oct 15

    Build a small web app that helps students form study groups.
    - Frontend in React (Priya said she'd take UI)
    - Backend API (Alex)
    - Auth + simple matching algorithm
    - Write a 4-page design doc first
    - Demo on Oct 12, final writeup Oct 15

    From chat:
    Priya: I can do the React screens this weekend
    Alex: I'll scaffold the API once the design doc is ready
    Sam: Happy to own the design doc and the final writeup
    """
    board = extract_board(
        sample,
        team_members=["Priya", "Alex", "Sam"],
        project_deadline="2025-10-15",
    )
    print(json.dumps(board.model_dump(), indent=2))
