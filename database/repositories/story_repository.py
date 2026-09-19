from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import StoryModel


class StoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        story_id: str,
        title: str,
        description: str = "",
    ) -> StoryModel:

        story = StoryModel(
            id=story_id,
            title=title,
            description=description,
        )

        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)

        return story

    def get(self, story_id: str) -> StoryModel | None:
        return self.db.get(StoryModel, story_id)

    def list(self) -> list[StoryModel]:
        return list(
            self.db.scalars(
                select(StoryModel)
            ).all()
        )