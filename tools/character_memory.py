from core.world import KnowledgeFact, WorldState


def get_character_knowledge(
    world_state: WorldState,
    character_id: str,
    sequence: int | None = None,
) -> list[KnowledgeFact]:
    return world_state.get_known_facts(
        character_id,
        sequence,
    )


def remember_fact(
    world_state: WorldState,
    fact: KnowledgeFact,
) -> None:
    world_state.knowledge[fact.id] = fact