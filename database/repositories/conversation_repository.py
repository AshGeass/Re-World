from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConversationMessage(BaseModel):
    conversation_id: str
    role: str
    content: str
    character_id: str | None = None
    branch_id: str | None = None
    timestamp: datetime = datetime.utcnow()


class ConversationRepository:
    """
    Temporary conversation-memory interface.

    Persistent implementation can later use PostgreSQL.
    """

    def __init__(self):
        self.messages: dict[str, list[ConversationMessage]] = {}

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        character_id: str | None = None,
        branch_id: str | None = None,
    ) -> ConversationMessage:

        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            character_id=character_id,
            branch_id=branch_id,
        )

        self.messages.setdefault(
            conversation_id,
            [],
        ).append(message)

        return message

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[ConversationMessage]:

        return self.messages.get(
            conversation_id,
            [],
        )