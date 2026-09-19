from __future__ import annotations

from ingestion import ingest_story


class StoryAnalystAgent:

    def __init__(self, llm=None):
        self.llm = llm

    def analyze(
        self,
        path: str,
        story_id: str,
    ):
        """
        Ingest and structurally analyze a story source.

        The current implementation uses deterministic extraction.
        LLM-based extraction can be plugged in later.
        """

        result = ingest_story(
            path=path,
            story_id=story_id,
        )

        return {
            "story_id": story_id,
            "source_path": result.source_path,
            "characters": result.characters,
            "events": result.events,
            "relationships": result.relationships,
            "timeline": result.timeline,
        }