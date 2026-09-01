#!/usr/bin/env python3
"""Extract a Cohort task board via Hugging Face. Requires HF_TOKEN."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import extract_board

SAMPLE_BRIEF = """
CS 450 — Collaborative Study Group Matcher
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
Priya: Demo video on the 12th.
"""


def main() -> None:
    print("Extracting board (Hugging Face)...\n")
    board = extract_board(
        SAMPLE_BRIEF,
        team_members=["Sam", "Priya", "Alex"],
        project_deadline="2025-10-15",
    )
    print(json.dumps(board.model_dump(), indent=2))
    print("\n--- Next actions ---")
    for a in board.suggested_next_actions:
        print(f"• {a}")


if __name__ == "__main__":
    main()
