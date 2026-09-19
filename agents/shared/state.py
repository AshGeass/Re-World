from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    story_id: str
    branch_id: str
    current_sequence: int = 0

    user_input: str = ""

    intent: str | None = None
    character_id: str | None = None

    retrieved_context: list[dict[str, Any]] = Field(default_factory=list)
    agent_output: str | None = None

    proposed_changes: list[dict[str, Any]] = Field(default_factory=list)
    contradictions: list[dict[str, Any]] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)