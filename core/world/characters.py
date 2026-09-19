from __future__ import annotations

from pydantic import BaseModel, Field


class CharacterState(BaseModel):
    id: str
    name: str

    aliases: list[str] = Field(default_factory=list)
    description: str = ""

    personality: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)

    current_location: str | None = None

    alive: bool = True

    knowledge_fact_ids: list[str] = Field(default_factory=list)

    relationship_ids: list[str] = Field(default_factory=list)

    metadata: dict[str, str] = Field(default_factory=dict)