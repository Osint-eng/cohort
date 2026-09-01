#!/usr/bin/env python3
"""Cohort Live Agent — interactive terminal REPL.

  export COHORT_MOCK=1   # or GEMINI_API_KEY in .env
  python examples/live_cli.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import BoardStore, extract_board, run_agent


def main() -> None:
    print("Cohort Live Agent")
    print("Paste a project brief (end with a blank line), or type commands.")
    print("Commands: check-in | list tasks | mark t1 complete | mark t2 blocked | quit\n")

    store: BoardStore | None = None

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            print("bye")
            break

        # Multi-line paste: if user types /paste, read until empty line
        if line.lower() == "/paste":
            print("(paste brief, then empty line)")
            chunks: list[str] = []
            while True:
                try:
                    row = input()
                except EOFError:
                    break
                if row.strip() == "":
                    break
                chunks.append(row)
            line = "\n".join(chunks)

        if store is None or len(line) > 280:
            print("agent> extracting board...")
            try:
                board = extract_board(
                    line,
                    team_members=["Sam", "Priya", "Alex"],
                )
                store = BoardStore(board)
                print(f"agent> board ready — {len(board.tasks)} tasks")
                for t in board.tasks:
                    print(
                        f"  [{t.id}] {t.title} (@{t.suggested_owner or 'unassigned'}) "
                        f"{t.status.value if hasattr(t.status, 'value') else t.status} "
                        f"due {t.due_date or '-'}"
                    )
            except Exception as e:
                print(f"agent> extract failed: {e}")
            continue

        reply = run_agent(line, store)
        print(f"agent> {reply}")
        if store.contribution_log:
            print("  log:", ", ".join(f"{e.actor} {e.action} {e.task_id}" for e in store.contribution_log))


if __name__ == "__main__":
    main()
