#!/usr/bin/env python3
"""
Example: Extract a Cohort task board from messy project input.

Requires:
  pip install anthropic pydantic python-dotenv
  export ANTHROPIC_API_KEY=sk-ant-...

Run:
  python examples/run_extraction.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import extract_board

SAMPLE_BRIEF = """
CS 450 — Collaborative Study Group Matcher
Due: 15 October

Deliverables:
1. Design document (4 pages max) — architecture + matching approach
2. Working web app (React frontend + simple backend)
3. Short demo video + final reflection

Team chat (excerpt):
Sam: I'll own the design doc. Need it done by Oct 5 so Alex can start the API.
Priya: Happy to take all the React UI. Can start as soon as we know the screens.
Alex: Backend + matching algorithm once design is locked.
Sam: Also happy to do the final reflection writeup.
Priya: Demo video we can film together on the 12th.

Professor note: matching algorithm can be simple (skills + availability).
Auth required. Host wherever is easiest.
"""


def main() -> None:
    print("Extracting board from sample brief + chat...\n")
    board = extract_board(
        SAMPLE_BRIEF,
        team_members=["Sam", "Priya", "Alex"],
        project_deadline="2025-10-15",
    )
    print(json.dumps(board.model_dump(), indent=2))
    print("\n--- Suggested next actions ---")
    for a in board.suggested_next_actions:
        print(f"• {a}")


if __name__ == "__main__":
    main()
