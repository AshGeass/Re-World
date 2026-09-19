from __future__ import annotations

from agents.shared import AgentResult
from core.simulation import (
    ConsistencyResult,
    Contradiction,
    ContradictionType,
)
from core.world import WorldState


class ConsistencyAgent:

    def __init__(self, llm=None):
        self.llm = llm

    def validate(
        self,
        world_state: WorldState,
    ) -> AgentResult:

        contradictions: list[Contradiction] = []

        contradictions.extend(
            self._check_timeline(world_state)
        )

        contradictions.extend(
            self._check_knowledge(world_state)
        )

        contradictions.extend(
            self._check_characters(world_state)
        )

        result = ConsistencyResult(
            valid=len(contradictions) == 0,
            contradictions=contradictions,
            checked_branch_id=world_state.branch_id,
            summary=(
                "No contradictions found."
                if not contradictions
                else f"Found {len(contradictions)} contradiction(s)."
            ),
        )

        return AgentResult(
            success=result.valid,
            output=result.summary,
            metadata={
                "consistency": result.model_dump(),
            },
        )

    def _check_timeline(
        self,
        state: WorldState,
    ) -> list[Contradiction]:

        contradictions = []

        sequences = [
            event.sequence
            for event in state.events.values()
        ]

        if any(sequence < 0 for sequence in sequences):
            contradictions.append(
                Contradiction(
                    type=ContradictionType.TIMELINE,
                    message="Event has an invalid timeline sequence.",
                )
            )

        return contradictions

    def _check_knowledge(
        self,
        state: WorldState,
    ) -> list[Contradiction]:

        contradictions = []

        current_sequence = (
            state.current_point.sequence
        )

        for fact in state.knowledge.values():

            if fact.valid_from_sequence > current_sequence:
                contradictions.append(
                    Contradiction(
                        type=ContradictionType.KNOWLEDGE,
                        message=(
                            f"Character {fact.character_id} "
                            "has knowledge from the future."
                        ),
                        character_ids=[fact.character_id],
                    )
                )

        return contradictions

    def _check_characters(
        self,
        state: WorldState,
    ) -> list[Contradiction]:

        contradictions = []

        for event in state.events.values():

            for character_id in event.participants:

                character = state.characters.get(
                    character_id
                )

                if character and not character.alive:
                    contradictions.append(
                        Contradiction(
                            type=ContradictionType.CHARACTER,
                            message=(
                                f"Dead character "
                                f"{character.name} participates "
                                f"in event '{event.title}'."
                            ),
                            event_ids=[event.id],
                            character_ids=[character_id],
                        )
                    )

        return contradictions