#!/usr/bin/env python3
"""
Example: Run the Cohort board agent after extraction.

Requires ANTHROPIC_API_KEY.
"""

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
    print("1. Extracting initial board...")
    board = extract_board(
        SAMPLE,
        team_members=["Sam", "Priya", "Alex"],
        project_deadline="2025-10-15",
    )
    store = BoardStore(board)
    print(f"   → {len(board.tasks)} tasks extracted\n")

    print("2. Asking agent for a selective check-in...")
    reply = run_agent(
        "Draft a short check-in message for anything that is late or blocked. "
        "If nothing is late yet, say so and list what's due soon.",
        store,
    )
    print(reply)
    print()

    print("3. Marking a task complete via agent...")
    if board.tasks:
        first_id = board.tasks[0].id
        reply2 = run_agent(
            f"Sam just finished the design doc. Mark task {first_id} as complete "
            f"and log the contribution.",
            store,
        )
        print(reply2)
        print()
        print("Contribution log:")
        for e in store.contribution_log:
            print(f"  • {e.actor} {e.action} {e.task_id} — {e.note or ''}")


if __name__ == "__main__":
    main()
