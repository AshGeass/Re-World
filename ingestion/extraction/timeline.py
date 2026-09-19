from __future__ import annotations

import re

from core.world.timeline import StoryPoint


def extract_timeline(text: str) -> list[StoryPoint]:
    """
    Fallback timeline extraction.

    Detects chapter/episode/part markers first. If none exist,
    creates timeline points from meaningful paragraphs.
    """

    points: list[StoryPoint] = []

    pattern = re.compile(
        r"(?im)^(chapter|episode|part|scene)\s+([^\n]+)"
    )

    matches = list(pattern.finditer(text))

    if matches:
        for index, match in enumerate(matches):
            kind = match.group(1).capitalize()
            label = match.group(2).strip()

            points.append(
                StoryPoint(
                    sequence=index + 1,
                    label=f"{kind} {label}",
                    chapter=label if kind == "Chapter" else None,
                    episode=label if kind == "Episode" else None,
                    description="",
                )
            )

        return points

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n+", text)
        if paragraph.strip()
    ]

    for index, paragraph in enumerate(paragraphs):
        sequence = index + 1

        first_sentence = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
            maxsplit=1,
        )[0]

        points.append(
            StoryPoint(
                sequence=sequence,
                label=first_sentence[:100] or f"Sequence {sequence}",
                description=paragraph[:500],
            )
        )

    if not points:
        points.append(
            StoryPoint(
                sequence=1,
                label="Beginning",
                description="Beginning of the source.",
            )
        )

    return points