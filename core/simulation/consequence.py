from __future__ import annotations

from pydantic import BaseModel, Field


class Consequence(BaseModel):
    id: str

    branch_id: str
    source_event_id: str | None = None

    title: str
    description: str

    affected_characters: list[str] = Field(default_factory=list)
    affected_events: list[str] = Field(default_factory=list)

    sequence: int = Field(ge=0)

    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    generated: bool = True