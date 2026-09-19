from __future__ import annotations

import logging

from agents.character.prompts import (
    SYSTEM_PROMPT,
    build_character_prompt,
)

from agents.shared import (
    AgentResult,
    CharacterRequest,
)

from tools.character_memory import (
    get_character_knowledge,
)

from tools.story_search import (
    search_story,
)

from tools.world_state import (
    get_world_state,
)

logger = logging.getLogger("reworld")


class CharacterAgent:

    def __init__(self, llm=None):

        if llm is not None:
            self.llm = llm
            return

        try:
            from config.llm import get_llm

            self.llm = get_llm()

        except Exception as exc:

            logger.warning(
                "LLM unavailable: %s",
                exc,
            )

            self.llm = None

    def respond(
        self,
        request: CharacterRequest,
    ) -> AgentResult:

        world_state = get_world_state(
            request.story_id,
            request.branch_id,
        )

        if world_state is None:

            return AgentResult(
                success=False,
                errors=[
                    "World state not found."
                ],
            )

        character = world_state.get_character(
            request.character_id
        )

        if character is None:

            return AgentResult(
                success=False,
                errors=[
                    "Character not found."
                ],
            )

        # Timeline-bounded memories.
        knowledge = get_character_knowledge(
            world_state,
            request.character_id,
            request.sequence,
        )

        # Character relationships.
        relationships = []

        for relationship in (
            world_state.relationships.values()
        ):

            if (
                relationship.character_a
                == character.id
                or
                relationship.character_b
                == character.id
            ):

                # Respect relationship validity.
                if (
                    relationship.valid_from_sequence
                    > request.sequence
                ):
                    continue

                if (
                    relationship.valid_until_sequence
                    is not None
                    and relationship.valid_until_sequence
                    < request.sequence
                ):
                    continue

                relationships.append(
                    relationship.model_dump()
                )

        # Retrieve source evidence.
        retrieved = search_story(
    request.message,
    limit=8,
    story_id=request.story_id,
)

        # Keep only evidence that belongs to this story
        # when metadata is available.
        source_evidence = []

        for result in retrieved:

            metadata = getattr(
                result,
                "metadata",
                None,
            )

            if isinstance(metadata, dict):

                result_story_id = metadata.get(
                    "story_id"
                )

                if (
                    result_story_id
                    and result_story_id
                    != request.story_id
                ):
                    continue

            source_evidence.append(
                getattr(
                    result,
                    "text",
                    str(result),
                )
            )

        emotional_state = character.metadata.get(
            "emotional_state",
            "unknown",
        )

        context = {
            "character": character.model_dump(),
            "personality": character.personality,
            "goals": character.goals,
            "current_location": character.current_location,
            "emotional_state": emotional_state,
            "relationships": relationships,
            "knowledge": [
                fact.model_dump()
                for fact in knowledge
            ],
            "source_evidence": source_evidence,
            "sequence": request.sequence,
            "user_message": request.message,
        }

        if self.llm is None:

            return AgentResult(
                success=True,
                output=(
                    f"{character.name} is ready to respond, "
                    "but the LLM provider is unavailable."
                ),
                metadata={
                    "context": context,
                    "character_id": character.id,
                    "sequence": request.sequence,
                },
            )

        try:

            response = self.llm.invoke(
                [
                    (
                        "system",
                        SYSTEM_PROMPT,
                    ),
                    (
                        "human",
                        build_character_prompt(
                            context
                        ),
                    ),
                ]
            )

            output_text = response.content

            if isinstance(
                output_text,
                list,
            ):

                output_text = "".join(
                    (
                        part.get("text", "")
                        if isinstance(part, dict)
                        else str(part)
                    )
                    for part in output_text
                )

            elif not isinstance(
                output_text,
                str,
            ):

                output_text = str(
                    output_text
                )

            return AgentResult(
                success=True,
                output=output_text,
                metadata={
                    "character_id": character.id,
                    "sequence": request.sequence,
                    "knowledge_count": len(
                        knowledge
                    ),
                    "context": context,
                },
            )

        except Exception as exc:

            logger.exception(
                "Character LLM error"
            )

            return AgentResult(
                success=False,
                output="",
                metadata={
                    "context": context,
                    "error": str(exc),
                },
                errors=[
                    f"Character LLM error: {exc}"
                ],
            )