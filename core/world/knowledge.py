from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Provenance(str, Enum):
    CANON = "canon"
    FANDOM = "fandom"
    GENERATED = "generated"


class KnowledgeFact(BaseModel):
    id: str
    character_id: str

    statement: str

    # The character cannot use this fact before this story point.
    valid_from_sequence: int = Field(default=0, ge=0)

    valid_until_sequence: int | None = None

    provenance: Provenance = Provenance.CANON

    source_refs: list[str] = Field(default_factory=list)

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    def is_known_at(self, sequence: int) -> bool:
        if sequence < self.valid_from_sequence:
            return False

        if (
            self.valid_until_sequence is not None
            and sequence > self.valid_until_sequence
        ):
            return False

        return True