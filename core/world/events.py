from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    PLOT = "plot"
    CHARACTER = "character"
    RELATIONSHIP = "relationship"
    LOCATION = "location"
    WORLD = "world"
    DIALOGUE = "dialogue"


class Event(BaseModel):
    id: str
    story_id: str
    title: str
    description: str

    sequence: int = Field(ge=0)
    event_type: EventType = EventType.PLOT

    participants: list[str] = Field(default_factory=list)
    location_id: Optional[str] = None

    source_refs: list[str] = Field(default_factory=list)

    canonical: bool = True
    branch_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)