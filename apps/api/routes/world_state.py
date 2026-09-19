from __future__ import annotations

from fastapi import APIRouter, HTTPException

from tools.world_state import get_world_state

router = APIRouter(prefix="/world-state", tags=["world-state"])


@router.get("/{story_id}/{branch_id}")
def world_state(story_id: str, branch_id: str):
    """Get the complete world state for a story/branch."""
    state = get_world_state(story_id, branch_id)
    if state is None:
        raise HTTPException(404, f"World state not found for {story_id}/{branch_id}")
    return state.model_dump()


@router.get("/{story_id}/{branch_id}/summary")
def world_summary(story_id: str, branch_id: str):
    """Get a summary of the world state."""
    state = get_world_state(story_id, branch_id)
    if state is None:
        raise HTTPException(404, "World state not found")

    return {
        "story_id": state.story_id,
        "branch_id": state.branch_id,
        "current_sequence": state.current_point.sequence,
        "current_label": state.current_point.label,
        "character_count": len(state.characters),
        "event_count": len(state.events),
        "relationship_count": len(state.relationships),
        "knowledge_count": len(state.knowledge),
        "location_count": len(state.locations),
        "version": state.version,
    }