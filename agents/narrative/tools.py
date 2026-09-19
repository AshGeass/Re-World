from tools.branch_manager import (
    clone_world_state,
    create_branch,
)
from tools.timeline import get_events_until
from tools.world_state import get_world_state


def create_alternate_timeline(
    story_id: str,
    branch_id: str,
    sequence: int,
    change: str,
):
    world_state = get_world_state(
        story_id,
        branch_id,
    )

    if world_state is None:
        raise ValueError("World state not found.")

    branch = create_branch(
        world_state,
        name=f"What If — {sequence}",
        description=change,
    )

    new_state = clone_world_state(
        world_state,
        branch,
    )

    affected_events = get_events_until(
        world_state,
        sequence,
    )

    return {
        "branch": branch,
        "world_state": new_state,
        "affected_events": affected_events,
    }