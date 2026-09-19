from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class Branch(BaseModel):
    id: str
    story_id: str

    name: str
    description: str = ""

    parent_branch_id: str | None = None
    divergence_event_id: str | None = None
    divergence_sequence: int = 0

    canonical: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)