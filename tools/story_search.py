from __future__ import annotations

from core.retrieval.search import SearchResult, StorySearch


_story_search = StorySearch()


def add_story_document(
    source_id: str,
    text: str,
    metadata: dict | None = None,
) -> None:
    _story_search.add_document(
        source_id,
        text,
        metadata,
    )


def search_story(
    query: str,
    limit: int = 5,
    story_id: str | None = None,
) -> list[SearchResult]:
    """
    Search story documents.

    When story_id is supplied, only documents belonging to that
    story should be returned.
    """

    results = _story_search.search(
        query,
        limit=max(limit * 3, limit),
    )

    if not story_id:
        return results[:limit]

    filtered = []

    for result in results:

        metadata = getattr(
            result,
            "metadata",
            None,
        )

        if not isinstance(metadata, dict):
            continue

        if metadata.get("story_id") == story_id:
            filtered.append(result)

        if len(filtered) >= limit:
            break

    return filtered