from __future__ import annotations

import logging
import os
import uuid

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from pydantic import BaseModel

from core.world import (
    KnowledgeFact,
    Provenance,
    StoryPoint,
    WorldState,
)

from ingestion.pipeline import (
    ingest_story,
    load_source,
)

from tools.story_search import (
    add_story_document,
)

from tools.world_state import (
    get_world_state,
    save_world_state,
)

logger = logging.getLogger("reworld")

router = APIRouter(
    prefix="/stories",
    tags=["stories"],
)


class StoryListItem(BaseModel):
    id: str
    title: str
    description: str = ""


class StoryListResponse(BaseModel):
    stories: list[StoryListItem]


class StoryCreateRequest(BaseModel):
    title: str
    raw_text: str
    description: str = ""


class StoryCreateResponse(BaseModel):
    story_id: str
    title: str
    characters: int
    events: int
    relationships: int
    timeline_points: int


@router.get(
    "/",
    response_model=StoryListResponse,
)
def list_stories():

    from tools.world_state import (
        _world_states,
    )

    stories = []
    seen = set()

    for ws in _world_states.values():

        story_id = ws.story_id

        if story_id in seen:
            continue

        seen.add(story_id)

        stories.append(
            StoryListItem(
                id=story_id,
                title=story_id.replace(
                    "_",
                    " ",
                ).replace(
                    "-",
                    " ",
                ).title(),
                description=(
                    f"World with "
                    f"{len(ws.characters)} characters "
                    f"and "
                    f"{len(ws.events)} events"
                ),
            )
        )

    return StoryListResponse(
        stories=stories
    )


@router.get("/{story_id}")
def get_story(
    story_id: str,
):

    ws = get_world_state(
        story_id,
        "canon",
    )

    if ws is None:
        raise HTTPException(
            404,
            f"Story '{story_id}' not found",
        )

    return {
        "story_id": ws.story_id,
        "branch_id": ws.branch_id,
        "characters": len(ws.characters),
        "events": len(ws.events),
        "relationships": len(ws.relationships),
        "knowledge_facts": len(ws.knowledge),
        "current_point": (
            ws.current_point.model_dump()
        ),
    }


def _build_world(
    text: str,
    story_id: str,
):

    temp_file = None

    # The extraction engine expects normalized text.
    # This helper uses the same Story Analyst path as uploads.
    from ingestion.normalization import (
        normalize_text,
    )

    from ingestion.extraction.story_analyzer import (
        extract_story,
    )

    normalized = normalize_text(text)

    (
        characters,
        events,
        relationships,
        timeline,
    ) = extract_story(
        normalized,
        story_id,
    )

    character_dict = {
        character.id: character
        for character in characters
    }

    event_dict = {
        event.id: event
        for event in events
    }

    relationship_dict = {
        relationship.id: relationship
        for relationship in relationships
    }

    knowledge = {}

    for event in events:

        for participant in event.participants:

            fact_id = (
                f"kf_{event.id}_{participant}"
            )

            knowledge[fact_id] = KnowledgeFact(
                id=fact_id,
                character_id=participant,
                statement=(
                    f"{event.title}: "
                    f"{event.description[:300]}"
                ),
                valid_from_sequence=(
                    event.sequence
                ),
                provenance=Provenance.CANON,
            )

    # Start the world at the FIRST point,
    # not the final point.
    if timeline:
        current_point = timeline[0]
    elif events:
        current_point = StoryPoint(
            sequence=events[0].sequence,
            label=events[0].title,
            description=events[0].description,
        )
    else:
        current_point = StoryPoint(
            sequence=1,
            label="Beginning",
            description="Beginning of the source.",
        )

    # Link knowledge IDs back to characters.
    for character in characters:

        character.knowledge_fact_ids = [
            fact.id
            for fact in knowledge.values()
            if fact.character_id
            == character.id
        ]

        character.relationship_ids = [
            relationship.id
            for relationship in relationships
            if (
                relationship.character_a
                == character.id
                or
                relationship.character_b
                == character.id
            )
        ]

    return WorldState(
        story_id=story_id,
        branch_id="canon",
        current_point=current_point,
        characters=character_dict,
        events=event_dict,
        relationships=relationship_dict,
        knowledge=knowledge,
    )


@router.post(
    "/",
    response_model=StoryCreateResponse,
)
def create_story(
    request: StoryCreateRequest,
):

    story_id = (
        request.title
        .lower()
        .replace(" ", "_")
        .replace("'", "")
    )

    story_id = (
        f"{story_id[:50]}_"
        f"{uuid.uuid4().hex[:6]}"
    )

    try:
        ws = _build_world(
            request.raw_text,
            story_id,
        )

    except Exception as exc:

        logger.exception(
            "Story analysis failed"
        )

        raise HTTPException(
            500,
            (
                "Story analysis failed: "
                f"{exc}"
            ),
        )

    save_world_state(ws)

    # Add source text to retrieval.
    paragraphs = [
        paragraph.strip()
        for paragraph in ws_to_paragraphs(
            request.raw_text
        )
        if paragraph.strip()
    ]

    for index, paragraph in enumerate(
        paragraphs
    ):

        add_story_document(
            source_id=(
                f"{story_id}_chunk_{index}"
            ),
            text=paragraph,
            metadata={
                "story_id": story_id,
                "chunk_index": index,
            },
        )

    return StoryCreateResponse(
        story_id=story_id,
        title=request.title,
        characters=len(ws.characters),
        events=len(ws.events),
        relationships=len(ws.relationships),
        timeline_points=len(
            {
                event.sequence
                for event in ws.events.values()
            }
        ),
    )


def ws_to_paragraphs(
    text: str,
) -> list[str]:

    return [
        part.strip()
        for part in text.split("\n\n")
        if part.strip()
    ]


@router.post(
    "/upload",
    response_model=StoryCreateResponse,
)
async def upload_story(
    file: UploadFile = File(...),
    title: str = Form(
        "Uploaded Story"
    ),
):

    content = await file.read()

    suffix = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if suffix == ".txt":

        text = content.decode(
            "utf-8",
            errors="replace",
        )

    elif suffix == ".pdf":

        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as tmp:

            tmp.write(content)
            tmp_path = tmp.name

        try:
            from ingestion.loaders.pdf import (
                load_pdf,
            )

            text = load_pdf(
                tmp_path
            )

        finally:
            os.unlink(tmp_path)

    elif suffix == ".docx":

        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".docx",
            delete=False,
        ) as tmp:

            tmp.write(content)
            tmp_path = tmp.name

        try:
            from ingestion.loaders.docx import (
                load_docx,
            )

            text = load_docx(
                tmp_path
            )

        finally:
            os.unlink(tmp_path)

    else:

        raise HTTPException(
            400,
            "Supported formats: TXT, PDF, DOCX",
        )

    request = StoryCreateRequest(
        title=title,
        raw_text=text,
    )

    return create_story(
        request
    )