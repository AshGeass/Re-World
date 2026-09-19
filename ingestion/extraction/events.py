from __future__ import annotations

import re

from core.world.events import Event, EventType


def extract_events(
    text: str,
    story_id: str,
) -> list[Event]:
    """
    Deterministic fallback event extraction.

    Main ingestion uses the Story Analyst LLM. This function remains
    available for compatibility and basic fallback behavior.
    """

    # Split on blank lines correctly.
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n+", text)
        if paragraph.strip()
    ]

    events: list[Event] = []

    for index, paragraph in enumerate(paragraphs):
        sequence = index + 1

        first_sentence = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
            maxsplit=1,
        )[0]

        title = first_sentence[:100].strip()

        events.append(
            Event(
                id=f"{story_id}_event_{sequence}",
                story_id=story_id,
                title=title or f"Event {sequence}",
                description=paragraph,
                sequence=sequence,
                event_type=EventType.PLOT,
            )
        )

    return events