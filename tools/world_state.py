from core.world import WorldState

_world_states: dict[str, WorldState] = {}


def save_world_state(state: WorldState) -> None:
    key = f"{state.story_id}:{state.branch_id}"
    _world_states[key] = state


def get_world_state(
    story_id: str,
    branch_id: str,
) -> WorldState | None:
    return _world_states.get(f"{story_id}:{branch_id}")


def update_world_state(state: WorldState) -> WorldState:
    save_world_state(state)
    return state