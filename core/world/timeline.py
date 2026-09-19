from __future__ import annotations

from pydantic import BaseModel, Field


class StoryPoint(BaseModel):
    sequence: int = Field(ge=0)

    label: str
    chapter: str | None = None
    episode: str | None = None

    description: str = ""


class TimelineNode(BaseModel):
    id: str

    story_id: str
    branch_id: str

    sequence: int = Field(ge=0)

    event_ids: list[str] = Field(default_factory=list)

    parent_node_id: str | None = None

    canonical: bool = True