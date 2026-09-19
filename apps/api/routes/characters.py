from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tools.world_state import get_world_state

router = APIRouter(prefix="/characters", tags=["characters"])


class CharacterResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    personality: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    current_location: str | None = None
    alive: bool = True
    aliases: list[str] = Field(default_factory=list)
    relationship_ids: list[str] = Field(default_factory=list)


class CharacterListResponse(BaseModel):
    characters: list[CharacterResponse]


@router.get("/{story_id}", response_model=CharacterListResponse)
def list_characters(story_id: str, branch_id: str = "canon"):
    """List all characters in a story world."""
    ws = get_world_state(story_id, branch_id)
    if ws is None:
        raise HTTPException(404, f"World state not found for story '{story_id}'")

    characters = [
        CharacterResponse(**c.model_dump())
        for c in ws.characters.values()
    ]
    return CharacterListResponse(characters=characters)


@router.get("/{story_id}/{character_id}", response_model=CharacterResponse)
def get_character(story_id: str, character_id: str, branch_id: str = "canon"):
    """Get a specific character."""
    ws = get_world_state(story_id, branch_id)
    if ws is None:
        raise HTTPException(404, f"World state not found")

    character = ws.get_character(character_id)
    if character is None:
        raise HTTPException(404, f"Character '{character_id}' not found")

    return CharacterResponse(**character.model_dump())


@router.get("/{story_id}/{character_id}/knowledge")
def get_character_knowledge(
    story_id: str,
    character_id: str,
    sequence: int = 0,
    branch_id: str = "canon",
):
    """Get knowledge facts available to a character at a given sequence."""
    ws = get_world_state(story_id, branch_id)
    if ws is None:
        raise HTTPException(404, "World state not found")

    facts = ws.get_known_facts(character_id, sequence)
    return {
        "character_id": character_id,
        "sequence": sequence,
        "facts": [f.model_dump() for f in facts],
        "total": len(facts),
    }