from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .characters import CharacterState
from .events import Event
from .knowledge import KnowledgeFact
from .relationships import RelationshipState
from .timeline import StoryPoint


class WorldState(BaseModel):
    story_id: str
    branch_id: str

    current_point: StoryPoint

    characters: dict[str, CharacterState] = Field(default_factory=dict)
    events: dict[str, Event] = Field(default_factory=dict)
    relationships: dict[str, RelationshipState] = Field(default_factory=dict)
    knowledge: dict[str, KnowledgeFact] = Field(default_factory=dict)

    locations: dict[str, str] = Field(default_factory=dict)

    version: int = 1

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_character(self, character_id: str) -> CharacterState | None:
        return self.characters.get(character_id)

    def get_known_facts(
        self,
        character_id: str,
        sequence: int | None = None,
    ) -> list[KnowledgeFact]:
        sequence = (
            sequence
            if sequence is not None
            else self.current_point.sequence
        )

        return [
            fact
            for fact in self.knowledge.values()
            if fact.character_id == character_id
            and fact.is_known_at(sequence)
        ]

    def add_event(self, event: Event) -> None:
        self.events[event.id] = event
        self.version += 1
        self.updated_at = datetime.utcnow()