#!/usr/bin/env python3
"""Run the Cohort board agent. Requires HF_TOKEN."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import BoardStore, extract_board, run_agent

SAMPLE = """
Group project: Build a study-group matcher.
Sam owns design doc (due Oct 5). Priya owns React UI.
Alex owns API + matching. Demo Oct 12, final due Oct 15.
"""


def main() -> None:
    print("1. Extracting board (Hugging Face)...")
    board = extract_board(
        SAMPLE,
        team_members=["Sam", "Priya", "Alex"],
        project_deadline="2025-10-15",
    )
    store = BoardStore(board)
    print(f"   → {len(board.tasks)} tasks\n")

    print("2. Check-in...")
    print(run_agent("Draft a check-in for late or blocked items.", store))
    print()

    if board.tasks:
        tid = board.tasks[0].id
        print("3. Mark complete...")
        print(run_agent(f"Sam finished task {tid}. Mark it complete.", store))
        print("\nContribution log:")
        for e in store.contribution_log:
            print(f"  • {e.actor} {e.action} {e.task_id}")


if __name__ == "__main__":
    main()
