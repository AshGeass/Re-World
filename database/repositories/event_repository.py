from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EventModel


class EventRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event_id: str,
        story_id: str,
        title: str,
        description: str,
        sequence: int,
        event_type: str = "plot",
        canonical: bool = True,
        branch_id: str | None = None,
    ) -> EventModel:

        event = EventModel(
            id=event_id,
            story_id=story_id,
            title=title,
            description=description,
            sequence=sequence,
            event_type=event_type,
            canonical=canonical,
            branch_id=branch_id,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def get(
        self,
        event_id: str,
    ) -> EventModel | None:

        return self.db.get(
            EventModel,
            event_id,
        )

    def list_by_story(
        self,
        story_id: str,
    ) -> list[EventModel]:

        return list(
            self.db.scalars(
                select(EventModel)
                .where(EventModel.story_id == story_id)
                .order_by(EventModel.sequence)
            ).all()
        )