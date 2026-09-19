from agents.router import RouterAgent
from agents.shared import RequestIntent


def test_router_detects_divergence():
    router = RouterAgent()

    result = router.route(
        "What if Eren did not attack?"
    )

    assert result.intent == RequestIntent.DIVERGENCE
    assert result.target_agent == "narrative"