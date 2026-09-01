"""Cohort Task Extraction Agent (Hugging Face).

Set token locally: export HF_TOKEN=hf_...
Never commit the token.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from .schemas import BoardProposal

load_dotenv()

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
DEFAULT_MODEL = os.environ.get("COHORT_HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")

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


def _get_client() -> InferenceClient:
    if not HF_TOKEN:
        raise RuntimeError(
            "Missing HF token. export HF_TOKEN=hf_... "
            "Create at https://huggingface.co/settings/tokens"
        )
    return InferenceClient(token=HF_TOKEN)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"No JSON found:\n{text[:500]}")
    return json.loads(text[start : end + 1])


def extract_board(
    source_text: str,
    *,
    team_members: list[str] | None = None,
    project_deadline: str | None = None,
    model: str | None = None,
    client: InferenceClient | None = None,
) -> BoardProposal:
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
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=2048,
            temperature=0.2,
        )
        raw = completion.choices[0].message.content or ""
    except Exception:
        prompt = SYSTEM_PROMPT + "\n\nUser:\n" + user_content + "\n\nAssistant:\n"
        raw = client.text_generation(
            prompt, model=model, max_new_tokens=2048, temperature=0.2
        )
    return BoardProposal.model_validate(_extract_json(raw))


def extract_board_as_dict(source_text: str, **kwargs: Any) -> dict[str, Any]:
    return extract_board(source_text, **kwargs).model_dump()
