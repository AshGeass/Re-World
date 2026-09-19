from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EventModel


class TimelineRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_events_until(
        self,
        story_id: str,
        sequence: int,
        branch_id: str | None = None,
    ) -> list[EventModel]:

        query = select(EventModel).where(
            EventModel.story_id == story_id,
            EventModel.sequence <= sequence,
        )

        if branch_id is not None:
            query = query.where(
                (EventModel.branch_id == branch_id)
                | (EventModel.canonical.is_(True))
            )

        query = query.order_by(EventModel.sequence)

        return list(self.db.scalars(query).all())