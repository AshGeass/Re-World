from tools.character_memory import get_character_knowledge
from tools.story_search import search_story
from tools.world_state import get_world_state


def get_character_context(
    story_id: str,
    branch_id: str,
    character_id: str,
    sequence: int,
    query: str,
) -> dict:

    world_state = get_world_state(
        story_id,
        branch_id,
    )

    if world_state is None:
        return {}

    character = world_state.get_character(
        character_id
    )

    knowledge = get_character_knowledge(
        world_state,
        character_id,
        sequence,
    )

    evidence = search_story(
        query,
        limit=5,
    )

    return {
        "character": character.model_dump()
        if character else None,
        "knowledge": [
            fact.model_dump()
            for fact in knowledge
        ],
        "evidence": [
            result.text
            for result in evidence
        ],
    }