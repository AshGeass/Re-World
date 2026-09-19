from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RequestIntent(str, Enum):
    CHAT = "chat"
    PERSPECTIVE = "perspective"
    DIVERGENCE = "divergence"
    EXPANSION = "expansion"
    INTERVIEW = "interview"
    MISSING_SCENE = "missing_scene"
    CROSSOVER = "crossover"
    UNKNOWN = "unknown"


class CharacterRequest(BaseModel):
    character_id: str
    story_id: str
    branch_id: str
    sequence: int = Field(ge=0)
    message: str


class NarrativeRequest(BaseModel):
    story_id: str
    branch_id: str
    sequence: int = Field(ge=0)
    change: str


class RouterDecision(BaseModel):
    intent: RequestIntent
    target_agent: str
    reason: str = ""


class AgentResult(BaseModel):
    success: bool
    output: str = ""
    metadata: dict = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)