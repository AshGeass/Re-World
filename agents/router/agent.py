from __future__ import annotations

from agents.shared import RequestIntent, RouterDecision


class RouterAgent:

    def __init__(self, llm=None):
        self.llm = llm

    def route(self, user_input: str) -> RouterDecision:
        text = user_input.lower()

        if any(
            word in text
            for word in ["what if", "change", "instead", "alternate"]
        ):
            return RouterDecision(
                intent=RequestIntent.DIVERGENCE,
                target_agent="narrative",
                reason="User wants to alter an event or explore an alternate timeline.",
            )

        if "perspective" in text or "point of view" in text:
            return RouterDecision(
                intent=RequestIntent.PERSPECTIVE,
                target_agent="character",
                reason="User requested a character perspective.",
            )

        if "interview" in text:
            return RouterDecision(
                intent=RequestIntent.INTERVIEW,
                target_agent="character",
                reason="User wants to interact directly with a character.",
            )

        if "missing scene" in text or "off-screen" in text:
            return RouterDecision(
                intent=RequestIntent.MISSING_SCENE,
                target_agent="narrative",
                reason="User wants a missing narrative section generated.",
            )

        if "crossover" in text:
            return RouterDecision(
                intent=RequestIntent.CROSSOVER,
                target_agent="narrative",
                reason="User wants a universe crossover.",
            )

        return RouterDecision(
            intent=RequestIntent.CHAT,
            target_agent="character",
            reason="Defaulting to character interaction.",
        )