import argparse

from ingestion import ingest_story


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a Re:World story source."
    )

    parser.add_argument("path")
    parser.add_argument("--story-id", required=True)

    args = parser.parse_args()

    result = ingest_story(
        args.path,
        args.story_id,
    )

    print(f"Source: {result.source_path}")
    print(f"Characters: {len(result.characters)}")
    print(f"Events: {len(result.events)}")
    print(f"Relationships: {len(result.relationships)}")
    print(f"Timeline points: {len(result.timeline)}")


if __name__ == "__main__":
    main()