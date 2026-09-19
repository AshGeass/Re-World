from __future__ import annotations

import json
import logging
import re

from core.world import (
    CharacterState,
    Event,
    EventType,
    RelationshipState,
    StoryPoint,
)

logger = logging.getLogger("reworld")


SYSTEM_PROMPT = """
You are the Story Analyst for Re:World.

Convert the supplied narrative into a structured story world.

STRICT RULES:
1. Only use information supported by the supplied source.
2. Never invent characters.
3. Never substitute characters from another story.
4. Detect characters in prose, narration, scripts and dialogue.
5. Detect meaningful narrative events in chronological order.
6. Detect relationships only when supported by the source.
7. Preserve chapter/episode information when present.
8. If chapters/episodes are absent, create meaningful chronological
   narrative checkpoints.
9. Emotional state may be extracted only when supported by the source.
10. If an emotional state is inferred, mark it as inferred.
11. Character knowledge must be compatible with the event sequence.
12. Return ONLY valid JSON.
"""


def _safe_id(value: str) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        value.lower(),
    ).strip("_")

    return value or "unknown"


def _clean_json(value: str) -> dict:
    value = value.strip()

    value = re.sub(
        r"^```(?:json)?\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\s*```$",
        "",
        value,
    )

    start = value.find("{")
    end = value.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "Story Analyst did not return valid JSON."
        )

    return json.loads(value[start:end + 1])


def _get_llm():
    from config.llm import get_llm

    return get_llm()


def analyze_story(
    text: str,
    story_id: str,
) -> dict:
    """
    Use Gemini to analyze the uploaded source once and produce
    characters, events, timeline and relationships together.
    """

    llm = _get_llm()

    prompt = f"""
Analyze this source for Re:World.

STORY ID:
{story_id}

SOURCE MATERIAL:
{text}

Return exactly this JSON structure:

{{
  "characters": [
    {{
      "id": "stable_snake_case_id",
      "name": "Actual name",
      "aliases": [],
      "description": "",
      "personality": [],
      "goals": [],
      "current_location": null,
      "alive": true,
      "emotional_state": "",
      "emotional_state_basis": "explicit|inferred|unknown"
    }}
  ],

  "events": [
    {{
      "id": "event_1",
      "title": "",
      "description": "",
      "sequence": 1,
      "event_type": "plot",
      "participants": [],
      "location": null,
      "source_ref": ""
    }}
  ],

  "timeline": [
    {{
      "sequence": 1,
      "label": "",
      "chapter": null,
      "episode": null,
      "description": ""
    }}
  ],

  "relationships": [
    {{
      "id": "",
      "character_a": "",
      "character_b": "",
      "relationship_type": "",
      "strength": 0.0,
      "description": "",
      "valid_from_sequence": 1,
      "valid_until_sequence": null,
      "source_ref": ""
    }}
  ]
}}

CHARACTER RULES:
- Include characters actually present in the source.
- A character mentioned in normal prose counts.
- Do not require NAME: dialogue format.
- If the source contains Luffy, Ace, Whitebeard and Akainu,
  extract those as four separate characters.
- Do not add other One Piece characters unless the source contains
  evidence for them.
- Preserve names and aliases from the source.

EVENT RULES:
- Extract actual narrative actions/events.
- Do not simply split every paragraph into an event.
- Combine sentences that describe the same event.
- Split distinct actions or turning points.
- Keep events chronological.
- Each event gets a sequence starting at 1.

TIMELINE RULES:
- Preserve Chapter/Episode/Part markers if present.
- Otherwise create useful chronological checkpoints.
- Never reduce a multi-event source to only "Beginning".

RELATIONSHIP RULES:
- Do not mark two characters as related merely because they appear
  in the same paragraph.
- Use evidence from the source.
- Use relationship types such as:
  family, friend, ally, enemy, rival, romantic, mentor,
  leader, subordinate, other.

EMOTION RULES:
- Only record emotional state supported by the source.
- If inferred, set emotional_state_basis to "inferred".
- Do not invent permanent personality traits from one sentence.
"""

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )

    content = response.content

    if isinstance(content, list):
        content = "".join(
            part.get("text", "")
            if isinstance(part, dict)
            else str(part)
            for part in content
        )

    return _clean_json(str(content))


def build_world_objects(
    data: dict,
    story_id: str,
):
    characters: list[CharacterState] = []

    for raw in data.get("characters", []):
        name = str(
            raw.get("name")
            or raw.get("id")
            or "Unknown Character"
        )

        character_id = _safe_id(
            str(raw.get("id") or name)
        )

        metadata: dict[str, str] = {}

        emotion = raw.get("emotional_state")
        emotion_basis = raw.get(
            "emotional_state_basis"
        )

        if emotion:
            metadata["emotional_state"] = str(
                emotion
            )

        if emotion_basis:
            metadata["emotional_state_basis"] = str(
                emotion_basis
            )

        characters.append(
            CharacterState(
                id=character_id,
                name=name,
                aliases=[
                    str(value)
                    for value in raw.get("aliases", [])
                    if value
                ],
                description=str(
                    raw.get("description") or ""
                ),
                personality=[
                    str(value)
                    for value in raw.get("personality", [])
                    if value
                ],
                goals=[
                    str(value)
                    for value in raw.get("goals", [])
                    if value
                ],
                current_location=(
                    str(raw["current_location"])
                    if raw.get("current_location")
                    else None
                ),
                alive=bool(
                    raw.get("alive", True)
                ),
                metadata=metadata,
            )
        )

    character_ids = {
        character.id
        for character in characters
    }

    events: list[Event] = []

    for index, raw in enumerate(
        data.get("events", [])
    ):
        sequence = int(
            raw.get("sequence", index + 1)
        )

        participants = [
            _safe_id(str(value))
            for value in raw.get(
                "participants",
                [],
            )
        ]

        participants = [
            value
            for value in participants
            if value in character_ids
        ]

        event_type_value = str(
            raw.get("event_type", "plot")
        ).lower()

        try:
            event_type = EventType(
                event_type_value
            )
        except ValueError:
            event_type = EventType.PLOT

        source_ref = raw.get("source_ref")

        events.append(
            Event(
                id=str(
                    raw.get("id")
                    or f"{story_id}_event_{sequence}"
                ),
                story_id=story_id,
                title=str(
                    raw.get("title")
                    or f"Event {sequence}"
                ),
                description=str(
                    raw.get("description") or ""
                ),
                sequence=sequence,
                event_type=event_type,
                participants=participants,
                location_id=(
                    str(raw["location"])
                    if raw.get("location")
                    else None
                ),
                source_refs=(
                    [str(source_ref)]
                    if source_ref
                    else []
                ),
            )
        )

    events.sort(
        key=lambda event: event.sequence
    )

    timeline: list[StoryPoint] = []

    for index, raw in enumerate(
        data.get("timeline", [])
    ):
        sequence = int(
            raw.get("sequence", index + 1)
        )

        timeline.append(
            StoryPoint(
                sequence=sequence,
                label=str(
                    raw.get("label")
                    or f"Sequence {sequence}"
                ),
                chapter=(
                    str(raw["chapter"])
                    if raw.get("chapter")
                    else None
                ),
                episode=(
                    str(raw["episode"])
                    if raw.get("episode")
                    else None
                ),
                description=str(
                    raw.get("description") or ""
                ),
            )
        )

    timeline.sort(
        key=lambda point: point.sequence
    )

    relationships: list[RelationshipState] = []

    for index, raw in enumerate(
        data.get("relationships", [])
    ):
        first = _safe_id(
            str(raw.get("character_a") or "")
        )
        second = _safe_id(
            str(raw.get("character_b") or "")
        )

        if (
            first not in character_ids
            or second not in character_ids
        ):
            continue

        strength = float(
            raw.get("strength", 0.0)
        )

        strength = max(
            -1.0,
            min(1.0, strength),
        )

        relationships.append(
            RelationshipState(
                id=str(
                    raw.get("id")
                    or f"{first}_{second}"
                ),
                character_a=first,
                character_b=second,
                relationship_type=str(
                    raw.get(
                        "relationship_type",
                        "other",
                    )
                ),
                strength=strength,
                description=str(
                    raw.get("description") or ""
                ),
                source_refs=(
                    [str(raw["source_ref"])]
                    if raw.get("source_ref")
                    else []
                ),
                valid_from_sequence=int(
                    raw.get(
                        "valid_from_sequence",
                        0,
                    )
                ),
                valid_until_sequence=(
                    int(
                        raw["valid_until_sequence"]
                    )
                    if raw.get(
                        "valid_until_sequence"
                    ) is not None
                    else None
                ),
            )
        )

    if not timeline and events:
        timeline = [
            StoryPoint(
                sequence=event.sequence,
                label=event.title,
                description=event.description,
            )
            for event in events
        ]

    return (
        characters,
        events,
        relationships,
        timeline,
    )


def extract_story(
    text: str,
    story_id: str,
):
    data = analyze_story(
        text,
        story_id,
    )

    return build_world_objects(
        data,
        story_id,
    )