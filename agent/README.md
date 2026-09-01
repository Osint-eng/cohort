# Cohort AI Agent

Claude-powered agent for the Cohort student-team workspace.

This follows patterns from the [Anthropic Claude Cookbooks](https://github.com/anthropics/claude-cookbooks) (`tool_use/` and structured extraction examples).

## What it does

1. **Structured extraction** (`extractor.py`)  
   Turns a brief, chat export, or notes into a validated task board (titles, owners, due dates, dependencies) via Claude tool use.

2. **Board agent** (`agent.py`)  
   Multi-turn tool-using agent that:
   - Lists tasks
   - Marks blocked / complete (with contribution log)
   - Drafts *selective* check-in messages (only late or blocked items)
   - Proposes reassignments

## Install

```bash
pip install anthropic pydantic python-dotenv
export ANTHROPIC_API_KEY=sk-ant-...
```

Optional: `COHORT_MODEL=claude-sonnet-4-5` (default).

## Quick start

```bash
# From repo root
python examples/run_extraction.py
python examples/run_agent.py
```

## Design principles (aligned with Cohort product)

| Principle | How the agent implements it |
|-----------|-----------------------------|
| Human in the loop | Extraction proposes; humans confirm on the board |
| Structured only | Tool schemas force JSON work items, never free-form essays |
| Selective nags | `draft_checkin` only surfaces late / blocked work |
| Trustworthy log | Every status change becomes a `ContributionEvent` |
| Model is a tool | The product is the board + log; Claude is the extraction/ops layer |

## File map

```
agent/
  schemas.py      # Pydantic models (Task, BoardProposal, ContributionEvent)
  extractor.py    # paste → board (tool-use structured extraction)
  agent.py        # multi-turn board agent + tools
  __init__.py
examples/
  run_extraction.py
  run_agent.py
```

## Extending

- Swap the in-memory `BoardStore` for your BaaS / database.
- Add tools: `invite_member`, `set_due_date`, `link_dependency`.
- Call `extract_board()` from your TanStack / API route when a user drops a brief.
