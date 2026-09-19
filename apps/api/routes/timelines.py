from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from tools.world_state import get_world_state

router = APIRouter(prefix="/timelines", tags=["timelines"])


class TimelineEvent(BaseModel):
    id: str
    title: str
    description: str
    sequence: int
    event_type: str = "plot"
    participants: list[str] = []
    canonical: bool = True
    branch_id: str | None = None


class TimelineResponse(BaseModel):
    story_id: str
    branch_id: str
    events: list[TimelineEvent]
    total_events: int
    max_sequence: int


@router.get("/{story_id}/{branch_id}", response_model=TimelineResponse)
def get_timeline(story_id: str, branch_id: str, up_to: int | None = None):
    """Get timeline events for a story, optionally up to a sequence point."""
    ws = get_world_state(story_id, branch_id)
    if ws is None:
        # If branch not found, try canon
        if branch_id != "canon":
            ws = get_world_state(story_id, "canon")
        if ws is None:
            raise HTTPException(404, f"Timeline not found for story '{story_id}'")

    events_list = sorted(ws.events.values(), key=lambda e: e.sequence)

    if up_to is not None:
        events_list = [e for e in events_list if e.sequence <= up_to]

    timeline_events = [
        TimelineEvent(
            id=e.id,
            title=e.title,
            description=e.description,
            sequence=e.sequence,
            event_type=e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type),
            participants=e.participants,
            canonical=e.canonical,
            branch_id=e.branch_id,
        )
        for e in events_list
    ]

    max_seq = max((e.sequence for e in events_list), default=0)

    return TimelineResponse(
        story_id=story_id,
        branch_id=branch_id,
        events=timeline_events,
        total_events=len(timeline_events),
        max_sequence=max_seq,
    )