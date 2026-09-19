from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import CharacterModel


class CharacterRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        character_id: str,
        story_id: str,
        name: str,
        description: str = "",
    ) -> CharacterModel:

        character = CharacterModel(
            id=character_id,
            story_id=story_id,
            name=name,
            description=description,
        )

        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)

        return character

    def get(
        self,
        character_id: str,
    ) -> CharacterModel | None:

        return self.db.get(
            CharacterModel,
            character_id,
        )

    def list_by_story(
        self,
        story_id: str,
    ) -> list[CharacterModel]:

        return list(
            self.db.scalars(
                select(CharacterModel).where(
                    CharacterModel.story_id == story_id
                )
            ).all()
        )