from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import KnowledgeFactModel


class KnowledgeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        fact_id: str,
        character_id: str,
        statement: str,
        valid_from_sequence: int = 0,
        valid_until_sequence: int | None = None,
        provenance: str = "canon",
        confidence: float = 1.0,
        source_refs: str = "",
    ) -> KnowledgeFactModel:

        fact = KnowledgeFactModel(
            id=fact_id,
            character_id=character_id,
            statement=statement,
            valid_from_sequence=valid_from_sequence,
            valid_until_sequence=valid_until_sequence,
            provenance=provenance,
            confidence=confidence,
            source_refs=source_refs,
        )

        self.db.add(fact)
        self.db.commit()
        self.db.refresh(fact)

        return fact

    def get_known_facts(
        self,
        character_id: str,
        sequence: int,
    ) -> list[KnowledgeFactModel]:

        query = select(KnowledgeFactModel).where(
            KnowledgeFactModel.character_id == character_id,
            KnowledgeFactModel.valid_from_sequence <= sequence,
        )

        query = query.where(
            (KnowledgeFactModel.valid_until_sequence.is_(None))
            | (
                KnowledgeFactModel.valid_until_sequence
                >= sequence
            )
        )

        return list(self.db.scalars(query).all())