from __future__ import annotations

from core.world import (
    CharacterState,
    Event,
    EventType,
    KnowledgeFact,
    Provenance,
    RelationshipState,
    StoryPoint,
    WorldState,
)
from tools.world_state import save_world_state
from tools.story_search import add_story_document

from database.connection import SessionLocal, init_db
from database.models import StoryModel


def seed_demo() -> None:
    story_id = "demo"
    branch_id = "canon"

    # Make sure DB exists
    init_db()

    # Make the story appear as Attack on Titan in the story list
    db = SessionLocal()
    try:
        story = db.get(StoryModel, story_id)

        if story is None:
            story = StoryModel(
                id=story_id,
                title="Attack on Titan",
                description="Demo story world for Re:World.",
            )
            db.add(story)
        else:
            story.title = "Attack on Titan"
            story.description = "Demo story world for Re:World."

        db.commit()
    finally:
        db.close()

    # -------------------------
    # CHARACTERS
    # -------------------------

    eren = CharacterState(
        id="eren",
        name="Eren Yeager",
        description="Determined, impulsive, freedom-driven.",
        personality=[
            "determined",
            "impulsive",
            "freedom-driven",
        ],
        goals=[
            "seek freedom",
            "protect his friends",
            "defend humanity",
        ],
        current_location="Trost",
        alive=True,
        aliases=["Eren"],
    )

    mikasa = CharacterState(
        id="mikasa",
        name="Mikasa Ackerman",
        description="Loyal, protective, calm under pressure.",
        personality=[
            "loyal",
            "protective",
            "calm under pressure",
        ],
        goals=[
            "protect Eren",
            "protect her comrades",
            "survive the battle",
        ],
        current_location="Trost",
        alive=True,
        aliases=["Mikasa"],
    )

    armin = CharacterState(
        id="armin",
        name="Armin Arlert",
        description="Intelligent, strategic, thoughtful.",
        personality=[
            "intelligent",
            "strategic",
            "thoughtful",
        ],
        goals=[
            "find a way to survive",
            "understand the Titans",
            "protect his friends",
        ],
        current_location="Trost",
        alive=True,
        aliases=["Armin"],
    )

    levi = CharacterState(
        id="levi",
        name="Levi Ackerman",
        description="Disciplined, blunt, highly capable.",
        personality=[
            "disciplined",
            "blunt",
            "decisive",
        ],
        goals=[
            "protect the Scouts",
            "complete the mission",
            "eliminate Titan threats",
        ],
        current_location="Trost",
        alive=True,
        aliases=["Levi"],
    )

    characters = {
        "eren": eren,
        "mikasa": mikasa,
        "armin": armin,
        "levi": levi,
    }

    # -------------------------
    # TIMELINE
    # -------------------------

    events = {
        "demo_event_1": Event(
            id="demo_event_1",
            story_id=story_id,
            title="The Battle of Trost",
            description=(
                "Eren, Mikasa, Armin, and the Scouts are fighting "
                "during the battle of Trost."
            ),
            sequence=1,
            event_type=EventType.PLOT,
            participants=["eren", "mikasa", "armin", "levi"],
            location_id="trost",
            source_refs=["demo"],
            canonical=True,
            branch_id=branch_id,
        ),
        "demo_event_2": Event(
            id="demo_event_2",
            story_id=story_id,
            title="The Titans Attack",
            description=(
                "Titans have breached the district and the Scouts "
                "are attempting to protect civilians."
            ),
            sequence=2,
            event_type=EventType.PLOT,
            participants=["eren", "mikasa", "armin"],
            location_id="trost",
            source_refs=["demo"],
            canonical=True,
            branch_id=branch_id,
        ),
        "demo_event_3": Event(
            id="demo_event_3",
            story_id=story_id,
            title="Eren Fights Back",
            description=(
                "Eren fights to protect his friends and the people "
                "inside the Walls."
            ),
            sequence=3,
            event_type=EventType.CHARACTER,
            participants=["eren", "mikasa"],
            location_id="trost",
            source_refs=["demo"],
            canonical=True,
            branch_id=branch_id,
        ),
    }

    # -------------------------
    # RELATIONSHIPS
    # -------------------------

    relationships = {
        "eren_mikasa": RelationshipState(
            id="eren_mikasa",
            character_a="eren",
            character_b="mikasa",
            relationship_type="close_family",
            strength=0.95,
            description="Mikasa is deeply protective of Eren.",
            source_refs=["demo"],
            valid_from_sequence=0,
        ),
        "eren_armin": RelationshipState(
            id="eren_armin",
            character_a="eren",
            character_b="armin",
            relationship_type="close_friends",
            strength=0.9,
            description="Eren and Armin are close childhood friends.",
            source_refs=["demo"],
            valid_from_sequence=0,
        ),
        "mikasa_armin": RelationshipState(
            id="mikasa_armin",
            character_a="mikasa",
            character_b="armin",
            relationship_type="comrades",
            strength=0.8,
            description="Mikasa trusts Armin as a close comrade.",
            source_refs=["demo"],
            valid_from_sequence=0,
        ),
    }

    # -------------------------
    # TIMELINE-BOUNDED KNOWLEDGE
    # -------------------------

    knowledge = {
        "eren_fact_1": KnowledgeFact(
            id="eren_fact_1",
            character_id="eren",
            statement=(
                "Eren is fighting to protect humanity and wants "
                "to understand the power of the Titans."
            ),
            valid_from_sequence=0,
            provenance=Provenance.CANON,
            source_refs=["demo"],
            confidence=1.0,
        ),
        "eren_fact_2": KnowledgeFact(
            id="eren_fact_2",
            character_id="eren",
            statement="The battle of Trost is currently underway.",
            valid_from_sequence=1,
            provenance=Provenance.CANON,
            source_refs=["demo"],
            confidence=1.0,
        ),
        "mikasa_fact_1": KnowledgeFact(
            id="mikasa_fact_1",
            character_id="mikasa",
            statement=(
                "Mikasa is focused on protecting Eren and "
                "surviving the battle of Trost."
            ),
            valid_from_sequence=0,
            provenance=Provenance.CANON,
            source_refs=["demo"],
            confidence=1.0,
        ),
        "armin_fact_1": KnowledgeFact(
            id="armin_fact_1",
            character_id="armin",
            statement=(
                "Armin is trying to understand the situation "
                "and find a strategy for survival."
            ),
            valid_from_sequence=0,
            provenance=Provenance.CANON,
            source_refs=["demo"],
            confidence=1.0,
        ),
        "levi_fact_1": KnowledgeFact(
            id="levi_fact_1",
            character_id="levi",
            statement=(
                "Levi is focused on completing the mission "
                "and protecting the Scouts."
            ),
            valid_from_sequence=0,
            provenance=Provenance.CANON,
            source_refs=["demo"],
            confidence=1.0,
        ),
    }

    # -------------------------
    # WORLD STATE
    # -------------------------

    world = WorldState(
        story_id=story_id,
        branch_id=branch_id,
        current_point=StoryPoint(
            sequence=1,
            label="Battle of Trost",
            episode="Demo Episode 1",
            description=(
                "The battle is underway and the Scouts are "
                "fighting to survive."
            ),
        ),
        characters=characters,
        events=events,
        relationships=relationships,
        knowledge=knowledge,
        locations={
            "trost": "Trost District",
        },
    )

    # IMPORTANT:
    # save_world_state overwrites the old Detective Hale world.
    save_world_state(world)

    # -------------------------
    # RETRIEVAL SOURCE
    # -------------------------

    documents = [
        (
            "Eren and Mikasa are fighting alongside the Scouts "
            "during the Battle of Trost."
        ),
        (
            "Eren is determined to protect his friends and "
            "fight for humanity and freedom."
        ),
        (
            "Mikasa is fiercely protective of Eren and her "
            "comrades during the battle."
        ),
        (
            "Armin uses strategy and observation to help the "
            "Scouts survive."
        ),
        (
            "Levi is a highly disciplined Scout focused on "
            "protecting his squad and completing missions."
        ),
        (
            "The battle of Trost is currently underway."
        ),
    ]

    for i, text in enumerate(documents):
        add_story_document(
            source_id=f"demo_aot_{i + 1}",
            text=text,
            metadata={
                "story_id": story_id,
                "sequence": 1,
                "source": "demo",
            },
        )

    print("Demo world seeded: Attack on Titan")
    print("Characters: Eren, Mikasa, Armin, Levi")
    print("Timeline: Battle of Trost")
    print("Branch: canon")


if __name__ == "__main__":
    seed_demo()