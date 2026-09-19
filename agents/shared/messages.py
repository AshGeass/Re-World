from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    agent: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)