from core.world import CharacterState, StoryPoint, WorldState


def test_character_state():
    character = CharacterState(
        id="test",
        name="Test Character",
    )

    assert character.name == "Test Character"


def test_world_state():
    state = WorldState(
        story_id="test",
        branch_id="canon",
        current_point=StoryPoint(
            sequence=0,
            label="Beginning",
        ),
    )

    assert state.story_id == "test"
    assert state.branch_id == "canon"