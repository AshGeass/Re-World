from core.world import StoryPoint, WorldState


def get_current_point(
    world_state: WorldState,
) -> StoryPoint:
    return world_state.current_point


def get_events_until(
    world_state: WorldState,
    sequence: int,
):
    return [
        event
        for event in world_state.events.values()
        if event.sequence <= sequence
    ]