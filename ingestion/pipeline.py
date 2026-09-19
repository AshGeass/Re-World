from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.world import (
    CharacterState,
    Event,
    RelationshipState,
    StoryPoint,
)

from .extraction.story_analyzer import (
    extract_story,
)

from .loaders import (
    load_docx,
    load_pdf,
    load_txt,
)

from .normalization import (
    normalize_text,
)


@dataclass
class IngestionResult:
    source_path: str
    text: str

    characters: list[CharacterState]
    events: list[Event]
    relationships: list[RelationshipState]
    timeline: list[StoryPoint]


def load_source(
    path: str | Path,
) -> str:
    path = Path(path)

    suffix = path.suffix.lower()

    if suffix == ".txt":
        return load_txt(path)

    if suffix == ".pdf":
        return load_pdf(path)

    if suffix == ".docx":
        return load_docx(path)

    raise ValueError(
        f"Unsupported source format: {suffix}"
    )


def ingest_story(
    path: str | Path,
    story_id: str,
) -> IngestionResult:

    raw_text = load_source(path)

    text = normalize_text(
        raw_text
    )

    (
        characters,
        events,
        relationships,
        timeline,
    ) = extract_story(
        text,
        story_id,
    )

    return IngestionResult(
        source_path=str(path),
        text=text,
        characters=characters,
        events=events,
        relationships=relationships,
        timeline=timeline,
    )