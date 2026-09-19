from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.shared import AgentResult, CharacterRequest

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("reworld")

# Lazy LLM + agent initialization
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.character import CharacterAgent
        try:
            from config.llm import get_llm
            llm = get_llm()
        except Exception as e:
            logger.warning(f"LLM unavailable, using fallback: {e}")
            llm = None
        _agent = CharacterAgent(llm=llm)
    return _agent


class ChatRequest(BaseModel):
    character_id: str
    story_id: str
    branch_id: str = "canon"
    sequence: int = Field(ge=0, default=0)
    message: str


class ChatResponse(BaseModel):
    success: bool
    output: str = ""
    character_id: str = ""
    sequence: int = 0
    knowledge_count: int = 0
    errors: list[str] = Field(default_factory=list)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat with a character at a specific timeline point."""
    agent = _get_agent()

    char_request = CharacterRequest(
        character_id=request.character_id,
        story_id=request.story_id,
        branch_id=request.branch_id,
        sequence=request.sequence,
        message=request.message,
    )

    result = agent.respond(char_request)

    knowledge_count = 0
    if result.metadata and "context" in result.metadata:
        knowledge_count = len(result.metadata["context"].get("knowledge", []))
    elif result.metadata:
        knowledge_count = result.metadata.get("knowledge_count", 0)

    return ChatResponse(
        success=result.success,
        output=result.output,
        character_id=request.character_id,
        sequence=request.sequence,
        knowledge_count=knowledge_count,
        errors=result.errors,
    )