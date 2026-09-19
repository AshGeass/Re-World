from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.shared import AgentResult, NarrativeRequest
from core.simulation import Branch, Consequence
from core.world import Event, EventType, Provenance, WorldState
from tools.branch_manager import create_branch, clone_world_state, get_branch, _branches
from tools.world_state import get_world_state, save_world_state

router = APIRouter(prefix="/branches", tags=["branches"])
logger = logging.getLogger("reworld")

# Lazy agent
_narrative_agent = None


def _get_narrative_agent():
    global _narrative_agent
    if _narrative_agent is None:
        from agents.narrative import NarrativeAgent
        try:
            from config.llm import get_llm
            llm = get_llm()
        except Exception:
            llm = None
        _narrative_agent = NarrativeAgent(llm=llm)
    return _narrative_agent


# ---------- Schemas ----------

class BranchCreateRequest(BaseModel):
    story_id: str
    parent_branch_id: str = "canon"
    sequence: int = Field(ge=0)
    change: str


class BranchInfo(BaseModel):
    id: str
    story_id: str
    name: str
    description: str = ""
    parent_branch_id: str | None = None
    divergence_event_id: str | None = None
    divergence_sequence: int = 0
    canonical: bool = False


class BranchCreateResponse(BaseModel):
    branch: BranchInfo
    affected_events: int
    affected_characters: list[str]
    consequence_description: str = ""


class DiffEntry(BaseModel):
    event_id: str
    title: str
    change_type: str  # added, removed, changed
    canon_description: str = ""
    branch_description: str = ""
    sequence: int = 0


class BranchDiffResponse(BaseModel):
    branch_id: str
    canon_branch_id: str
    events_added: list[DiffEntry]
    events_removed: list[DiffEntry]
    events_changed: list[DiffEntry]
    characters_affected: list[str]
    relationships_changed: int
    ripple_depth: int
    total_changes: int


class ConsistencyIssue(BaseModel):
    type: str
    message: str
    event_ids: list[str] = Field(default_factory=list)
    character_ids: list[str] = Field(default_factory=list)
    severity: str = "warning"


class ConsistencyResponse(BaseModel):
    valid: bool
    branch_id: str
    issues: list[ConsistencyIssue]
    summary: str


# ---------- Routes ----------

@router.get("/")
def list_branches(story_id: str):
    """List all branches for a story."""
    branches = [
        BranchInfo(
            id=b.id,
            story_id=b.story_id,
            name=b.name,
            description=b.description,
            parent_branch_id=b.parent_branch_id,
            divergence_event_id=b.divergence_event_id,
            divergence_sequence=b.divergence_sequence,
            canonical=b.canonical,
        )
        for b in _branches.values()
        if b.story_id == story_id
    ]
    return {"branches": branches}


@router.post("/create", response_model=BranchCreateResponse)
def create_new_branch(request: BranchCreateRequest):
    """Create a What-If branch at a specific divergence point."""
    ws = get_world_state(request.story_id, request.parent_branch_id)
    if ws is None:
        raise HTTPException(404, "World state not found")

    # Find the divergence event
    divergence_event = None
    for event in ws.events.values():
        if event.sequence == request.sequence:
            divergence_event = event
            break

    # Create branch
    branch = create_branch(
        world_state=ws,
        name=f"What If — {request.change[:60]}",
        description=request.change,
        divergence_event_id=divergence_event.id if divergence_event else None,
        divergence_sequence=request.sequence,
    )

    # Clone world state for the branch
    branch_ws = clone_world_state(ws, branch)

    # Identify affected events (events at or after divergence)
    affected_events = [
        e for e in ws.events.values()
        if e.sequence >= request.sequence
    ]

    # Identify affected characters
    affected_char_ids = set()
    for e in affected_events:
        affected_char_ids.update(e.participants)

    # Create a consequence event on the branch
    consequence_id = f"branch_{branch.id[:8]}_consequence_1"
    consequence_event = Event(
        id=consequence_id,
        story_id=request.story_id,
        title=f"Divergence: {request.change[:80]}",
        description=f"In this alternate timeline: {request.change}",
        sequence=request.sequence,
        event_type=EventType.PLOT,
        participants=list(affected_char_ids)[:5],
        canonical=False,
        branch_id=branch.id,
    )
    branch_ws.add_event(consequence_event)

    # Save the branch world state
    save_world_state(branch_ws)

    return BranchCreateResponse(
        branch=BranchInfo(
            id=branch.id,
            story_id=branch.story_id,
            name=branch.name,
            description=branch.description,
            parent_branch_id=branch.parent_branch_id,
            divergence_event_id=branch.divergence_event_id,
            divergence_sequence=branch.divergence_sequence,
        ),
        affected_events=len(affected_events),
        affected_characters=list(affected_char_ids),
        consequence_description=request.change,
    )


@router.post("/diverge")
def diverge(request: NarrativeRequest):
    """Legacy diverge endpoint using NarrativeAgent."""
    agent = _get_narrative_agent()
    result = agent.diverge(request)
    return result.model_dump()


@router.get("/{branch_id}")
def get_branch_info(branch_id: str):
    """Get branch details."""
    branch = get_branch(branch_id)
    if branch is None:
        raise HTTPException(404, "Branch not found")
    return BranchInfo(
        id=branch.id,
        story_id=branch.story_id,
        name=branch.name,
        description=branch.description,
        parent_branch_id=branch.parent_branch_id,
        divergence_event_id=branch.divergence_event_id,
        divergence_sequence=branch.divergence_sequence,
        canonical=branch.canonical,
    )


@router.get("/{branch_id}/diff", response_model=BranchDiffResponse)
def get_branch_diff(branch_id: str):
    """Compare a branch against canon."""
    branch = get_branch(branch_id)
    if branch is None:
        raise HTTPException(404, "Branch not found")

    # Get branch world state
    branch_ws = get_world_state(branch.story_id, branch_id)
    if branch_ws is None:
        raise HTTPException(404, "Branch world state not found")

    # Get canon world state
    parent_id = branch.parent_branch_id or "canon"
    canon_ws = get_world_state(branch.story_id, parent_id)
    if canon_ws is None:
        raise HTTPException(404, "Canon world state not found")

    # Compute diff
    canon_events = set(canon_ws.events.keys())
    branch_events = set(branch_ws.events.keys())

    added_ids = branch_events - canon_events
    removed_ids = canon_events - branch_events
    common_ids = canon_events & branch_events

    events_added = []
    for eid in added_ids:
        e = branch_ws.events[eid]
        events_added.append(DiffEntry(
            event_id=eid,
            title=e.title,
            change_type="added",
            branch_description=e.description,
            sequence=e.sequence,
        ))

    events_removed = []
    for eid in removed_ids:
        e = canon_ws.events[eid]
        events_removed.append(DiffEntry(
            event_id=eid,
            title=e.title,
            change_type="removed",
            canon_description=e.description,
            sequence=e.sequence,
        ))

    events_changed = []
    for eid in common_ids:
        ce = canon_ws.events[eid]
        be = branch_ws.events[eid]
        if ce.description != be.description or ce.title != be.title:
            events_changed.append(DiffEntry(
                event_id=eid,
                title=be.title,
                change_type="changed",
                canon_description=ce.description,
                branch_description=be.description,
                sequence=be.sequence,
            ))

    # Characters affected
    affected_chars = set()
    for e in events_added + events_changed:
        be = branch_ws.events.get(e.event_id)
        if be and hasattr(be, 'participants'):
            affected_chars.update(be.participants)

    # Relationships changed
    canon_rels = set(canon_ws.relationships.keys())
    branch_rels = set(branch_ws.relationships.keys())
    rel_changes = len(canon_rels.symmetric_difference(branch_rels))

    # Ripple depth: how many events after divergence are affected
    ripple = len(events_added) + len(events_changed)

    total = len(events_added) + len(events_removed) + len(events_changed)

    return BranchDiffResponse(
        branch_id=branch_id,
        canon_branch_id=parent_id,
        events_added=events_added,
        events_removed=events_removed,
        events_changed=events_changed,
        characters_affected=list(affected_chars),
        relationships_changed=rel_changes,
        ripple_depth=ripple,
        total_changes=total,
    )


@router.post("/{branch_id}/validate", response_model=ConsistencyResponse)
def validate_branch(branch_id: str):
    """Run consistency checks on a branch."""
    branch = get_branch(branch_id)
    if branch is None:
        raise HTTPException(404, "Branch not found")

    branch_ws = get_world_state(branch.story_id, branch_id)
    if branch_ws is None:
        raise HTTPException(404, "Branch world state not found")

    from agents.consistency import ConsistencyAgent
    agent = ConsistencyAgent()
    result = agent.validate(branch_ws)

    issues = []
    if result.metadata and "consistency" in result.metadata:
        cons = result.metadata["consistency"]
        for c in cons.get("contradictions", []):
            issues.append(ConsistencyIssue(
                type=c.get("type", "unknown"),
                message=c.get("message", ""),
                event_ids=c.get("event_ids", []),
                character_ids=c.get("character_ids", []),
                severity=c.get("severity", "warning"),
            ))

    return ConsistencyResponse(
        valid=result.success,
        branch_id=branch_id,
        issues=issues,
        summary=result.output,
    )