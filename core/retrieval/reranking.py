from __future__ import annotations

from .search import SearchResult


class Reranker:
    """
    Basic retrieval reranking interface.

    Can later be replaced with an LLM or cross-encoder reranker.
    """

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        limit: int = 5,
    ) -> list[SearchResult]:

        query_words = set(query.lower().split())

        ranked = []

        for result in results:
            text_words = set(result.text.lower().split())

            overlap = len(query_words & text_words)

            ranked.append(
                (
                    overlap,
                    result,
                )
            )

        ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [result for _, result in ranked[:limit]]