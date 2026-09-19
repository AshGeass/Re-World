from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class StoryModel(Base):
    __tablename__ = "stories"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    characters: Mapped[list["CharacterModel"]] = relationship(
        back_populates="story",
        cascade="all, delete-orphan",
    )

    events: Mapped[list["EventModel"]] = relationship(
        back_populates="story",
        cascade="all, delete-orphan",
    )


class CharacterModel(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    story_id: Mapped[str] = mapped_column(
        ForeignKey("stories.id"),
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    alive: Mapped[bool] = mapped_column(Boolean, default=True)
    current_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    story: Mapped["StoryModel"] = relationship(
        back_populates="characters",
    )


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    story_id: Mapped[str] = mapped_column(
        ForeignKey("stories.id"),
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    sequence: Mapped[int] = mapped_column(Integer, index=True)

    event_type: Mapped[str] = mapped_column(
        String(100),
        default="plot",
    )

    canonical: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    branch_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    story: Mapped["StoryModel"] = relationship(
        back_populates="events",
    )


class BranchModel(Base):
    __tablename__ = "branches"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    story_id: Mapped[str] = mapped_column(
        ForeignKey("stories.id"),
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255))

    description: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    parent_branch_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    divergence_event_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    divergence_sequence: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    canonical: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class KnowledgeFactModel(Base):
    __tablename__ = "knowledge_facts"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"),
        index=True,
    )

    statement: Mapped[str] = mapped_column(Text)

    valid_from_sequence: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    valid_until_sequence: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    provenance: Mapped[str] = mapped_column(
        String(50),
        default="canon",
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
    )

    source_refs: Mapped[str] = mapped_column(
        Text,
        default="",
    )