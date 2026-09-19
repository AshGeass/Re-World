from __future__ import annotations

import re

from core.world.relationships import RelationshipState


def _normalize_id(value: str) -> str:
    return (
        re.sub(r"[^a-z0-9]+", "_", value.lower())
        .strip("_")
    )


def extract_relationships(
    text: str,
    character_ids: list[str],
) -> list[RelationshipState]:
    """
    Fallback relationship extraction.

    The Story Analyst is the primary extractor. This fallback only
    creates a relationship when two known characters repeatedly occur
    near one another in the source.
    """

    relationships: list[RelationshipState] = []

    lowered = text.lower()

    for index, first in enumerate(character_ids):
        for second in character_ids[index + 1:]:
            first_name = first.replace("_", " ").lower()
            second_name = second.replace("_", " ").lower()

            if not first_name or not second_name:
                continue

            first_count = lowered.count(first_name)
            second_count = lowered.count(second_name)

            if first_count == 0 or second_count == 0:
                continue

            relationship_id = f"{first}_{second}"

            relationships.append(
                RelationshipState(
                    id=relationship_id,
                    character_a=first,
                    character_b=second,
                    relationship_type="associated",
                    strength=0.0,
                    description=(
                        "The source contains both characters. "
                        "Relationship type requires narrative evidence."
                    ),
                    source_refs=[],
                    valid_from_sequence=0,
                )
            )

    return relationships