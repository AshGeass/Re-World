from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchResult:
    source_id: str
    text: str
    score: float
    metadata: dict


class StorySearch:
    """
    Retrieval interface for story-source passages.

    The actual vector database implementation can be plugged in later.
    """

    def __init__(self) -> None:
        self._documents: list[SearchResult] = []

    def add_document(
        self,
        source_id: str,
        text: str,
        metadata: dict | None = None,
    ) -> None:
        self._documents.append(
            SearchResult(
                source_id=source_id,
                text=text,
                score=1.0,
                metadata=metadata or {},
            )
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchResult]:
        if not query.strip():
            return []

        query_words = set(query.lower().split())

        scored = []

        for document in self._documents:
            words = set(document.text.lower().split())

            overlap = len(query_words & words)

            if overlap > 0:
                scored.append(
                    SearchResult(
                        source_id=document.source_id,
                        text=document.text,
                        score=float(overlap),
                        metadata=document.metadata,
                    )
                )

        scored.sort(key=lambda result: result.score, reverse=True)

        return scored[:limit]