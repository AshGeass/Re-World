from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BranchModel


class BranchRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        branch_id: str,
        story_id: str,
        name: str,
        description: str = "",
        parent_branch_id: str | None = None,
        divergence_event_id: str | None = None,
        divergence_sequence: int = 0,
    ) -> BranchModel:

        branch = BranchModel(
            id=branch_id,
            story_id=story_id,
            name=name,
            description=description,
            parent_branch_id=parent_branch_id,
            divergence_event_id=divergence_event_id,
            divergence_sequence=divergence_sequence,
        )

        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)

        return branch

    def get(
        self,
        branch_id: str,
    ) -> BranchModel | None:

        return self.db.get(
            BranchModel,
            branch_id,
        )

    def list_by_story(
        self,
        story_id: str,
    ) -> list[BranchModel]:

        return list(
            self.db.scalars(
                select(BranchModel).where(
                    BranchModel.story_id == story_id
                )
            ).all()
        )