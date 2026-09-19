from core.simulation import Branch


def test_branch():
    branch = Branch(
        id="branch-1",
        story_id="story-1",
        name="Alternate Timeline",
    )

    assert branch.canonical is False
    assert branch.story_id == "story-1"