"""Pydantic schemas for Cohort structured outputs."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Task(BaseModel):
    """A single work item on the Cohort board."""

    id: str = Field(description="Short stable id, e.g. t1, t2")
    title: str = Field(description="Clear, action-oriented task title")
    description: str = Field(
        default="",
        description="One or two sentences of context or acceptance criteria",
    )
    suggested_owner: Optional[str] = Field(
        default=None,
        description="Name or handle of the person who should own this task",
    )
    due_date: Optional[str] = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) if a deadline can be inferred",
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="List of task ids this task depends on",
    )
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: str = Field(
        default="medium",
        description="low | medium | high",
    )


class BoardProposal(BaseModel):
    """Full proposed task board extracted from unstructured input."""

    project_summary: str = Field(
        description="One-paragraph summary of what the project is about"
    )
    tasks: list[Task] = Field(description="Ordered list of extracted tasks")
    open_questions: list[str] = Field(
        default_factory=list,
        description="Ambiguities or missing info the team should resolve",
    )
    suggested_next_actions: list[str] = Field(
        default_factory=list,
        description="Immediate next steps for the team",
    )


class ContributionEvent(BaseModel):
    """A single event in the contribution log."""

    actor: str
    action: str = Field(description="accepted | completed | unblocked | reassigned")
    task_id: str
    note: Optional[str] = None
    timestamp: Optional[str] = None
