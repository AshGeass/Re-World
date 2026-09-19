from __future__ import annotations

from pydantic import BaseModel, Field


class RelationshipState(BaseModel):
    id: str

    character_a: str
    character_b: str

    relationship_type: str
    strength: float = Field(default=0.0, ge=-1.0, le=1.0)

    description: str = ""

    source_refs: list[str] = Field(default_factory=list)

    valid_from_sequence: int = 0
    valid_until_sequence: int | None = None