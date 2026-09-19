from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ContradictionType(str, Enum):
    TIMELINE = "timeline"
    KNOWLEDGE = "knowledge"
    CHARACTER = "character"
    RELATIONSHIP = "relationship"
    LOCATION = "location"
    DUPLICATE_EVENT = "duplicate_event"


class Contradiction(BaseModel):
    type: ContradictionType

    message: str

    event_ids: list[str] = Field(default_factory=list)
    character_ids: list[str] = Field(default_factory=list)

    severity: str = "warning"


class ConsistencyResult(BaseModel):
    valid: bool

    contradictions: list[Contradiction] = Field(default_factory=list)

    checked_branch_id: str

    summary: str = ""