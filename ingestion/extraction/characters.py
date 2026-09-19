from __future__ import annotations

import re

from core.world.characters import CharacterState


def _make_id(name: str) -> str:
    return (
        re.sub(r"[^a-z0-9]+", "_", name.lower())
        .strip("_")
        or "character"
    )


def extract_characters(text: str) -> list[CharacterState]:
    """
    Lightweight fallback character extraction.

    The main ingestion path uses Story Analyst LLM extraction.
    This fallback handles common prose and script formats.
    """

    characters: dict[str, CharacterState] = {}

    # Script/dialogue format:
    # LUFFY: ...
    dialogue_pattern = re.compile(
        r"(?m)^([A-Z][A-Za-z0-9 _'-]{1,40}):\s*"
    )

    # Common narrative names after verbs/prepositions.
    prose_pattern = re.compile(
        r"\b(?:"
        r"(?:Captain|Commander|Admiral|Dr\.|Doctor|Mr\.|Mrs\.|Ms\.)\s+"
        r")?"
        r"([A-Z][a-z]{2,20}(?:\s+[A-Z][a-z]{2,20}){0,2})"
        r"\b"
    )

    candidates: list[str] = []

    for match in dialogue_pattern.finditer(text):
        candidates.append(match.group(1).strip())

    for match in prose_pattern.finditer(text):
        name = match.group(1).strip()

        # Ignore obvious sentence-start/common words.
        if name.lower() in {
            "the",
            "this",
            "that",
            "when",
            "then",
            "after",
            "before",
            "however",
            "chapter",
            "episode",
            "part",
        }:
            continue

        candidates.append(name)

    for name in candidates:
        character_id = _make_id(name)

        if character_id not in characters:
            characters[character_id] = CharacterState(
                id=character_id,
                name=name,
            )

    return list(characters.values())