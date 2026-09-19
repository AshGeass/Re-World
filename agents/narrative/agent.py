from __future__ import annotations

import uuid

from agents.shared import AgentResult, NarrativeRequest
from agents.narrative.prompts import SYSTEM_PROMPT
from core.simulation import Consequence
from core.world import Event, EventType
from tools.branch_manager import create_branch, clone_world_state
from tools.timeline import get_events_until
from tools.world_state import get_world_state, save_world_state


class NarrativeAgent:

    def __init__(self, llm=None):
        self.llm = llm

    def diverge(self, request: NarrativeRequest) -> AgentResult:

        world_state = get_world_state(
            request.story_id,
            request.branch_id,
        )

        if world_state is None:
            return AgentResult(
                success=False,
                errors=["World state not found."],
            )

        branch = create_branch(
            world_state=world_state,
            name=f"What If — {request.change[:60]}",
            description=request.change,
            divergence_sequence=request.sequence,
        )

        new_state = clone_world_state(world_state, branch)

        affected_events = get_events_until(
            world_state, request.sequence,
        )

        consequence = Consequence(
            id=str(uuid.uuid4()),
            branch_id=branch.id,
            title="Timeline Divergence",
            description=request.change,
            affected_events=[e.id for e in affected_events],
            affected_characters=list({
                char_id
                for e in affected_events
                for char_id in e.participants
            }),
            sequence=request.sequence,
            confidence=0.5,
        )

        # FIX: Insert a proper Event object, not a raw dict
        divergence_event = Event(
            id=f"branch_{branch.id[:8]}_divergence",
            story_id=request.story_id,
            title=f"Divergence: {request.change[:80]}",
            description=f"In this alternate timeline: {request.change}",
            sequence=request.sequence,
            event_type=EventType.PLOT,
            participants=consequence.affected_characters[:5],
            canonical=False,
            branch_id=branch.id,
        )
        new_state.add_event(divergence_event)

        # Save the branch world state so it can be retrieved later
        save_world_state(new_state)

        if self.llm is None:
            return AgentResult(
                success=True,
                output=f"Created alternate branch '{branch.name}'.",
                metadata={
                    "branch_id": branch.id,
                    "consequence": consequence.model_dump(),
                    "affected_events": len(affected_events),
                    "affected_characters": consequence.affected_characters,
                },
            )

        prompt = self._build_prompt(request, world_state, affected_events)

        response = self.llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("human", prompt),
        ])

        return AgentResult(
            success=True,
            output=response.content if hasattr(response, 'content') else str(response),
            metadata={
                "branch_id": branch.id,
                "consequence": consequence.model_dump(),
                "affected_events": len(affected_events),
                "affected_characters": consequence.affected_characters,
            },
        )

    def _build_prompt(self, request, world_state, affected_events) -> str:
        event_summaries = "\n".join(
            f"- [{e.sequence}] {e.title}: {e.description[:120]}"
            for e in affected_events
        )
        char_summaries = "\n".join(
            f"- {c.name}: {c.description[:100]}"
            for c in world_state.characters.values()
        )
        return f"""Story: {request.story_id}
Timeline divergence point: sequence {request.sequence}

User's change:
{request.change}

Characters in this world:
{char_summaries}

Events up to the divergence point:
{event_summaries}

Simulate the downstream consequences of this change.

Return:
- Immediate effects on characters and relationships
- Changed events that would now play out differently
- New events that would occur as a result
- Likely future consequences

Do not alter the canonical timeline.
Clearly distinguish generated consequences from canon.
Be specific about which characters and events are affected."""