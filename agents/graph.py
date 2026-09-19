"""LangGraph multi-agent workflow for Re:World.

Graph: START → router → [character → END | narrative → consistency → END]

Agents receive the shared LLM via lazy initialization to avoid
import-time crashes when GOOGLE_API_KEY is not yet available.
"""
from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph

from agents.shared import AgentState, CharacterRequest, NarrativeRequest

logger = logging.getLogger("reworld")

# ── Lazy agent singletons ────────────────────────────────────

_llm = None
_llm_loaded = False


def _get_llm():
    global _llm, _llm_loaded
    if not _llm_loaded:
        _llm_loaded = True
        try:
            from config.llm import get_llm
            _llm = get_llm()
            logger.info("LLM loaded for agent graph.")
        except Exception as e:
            logger.warning(f"LLM unavailable in graph, agents will use fallback: {e}")
            _llm = None
    return _llm


_agents: dict = {}


def _get_agent(name: str):
    if name not in _agents:
        llm = _get_llm()
        if name == "router":
            from agents.router import RouterAgent
            _agents[name] = RouterAgent(llm=llm)
        elif name == "character":
            from agents.character import CharacterAgent
            _agents[name] = CharacterAgent(llm=llm)
        elif name == "narrative":
            from agents.narrative import NarrativeAgent
            _agents[name] = NarrativeAgent(llm=llm)
        elif name == "consistency":
            from agents.consistency import ConsistencyAgent
            _agents[name] = ConsistencyAgent(llm=llm)
    return _agents[name]


# ── Node functions ───────────────────────────────────────────

def route_request(state: AgentState):
    router = _get_agent("router")
    decision = router.route(state.user_input)
    return {
        "intent": decision.intent.value,
        "metadata": {
            **state.metadata,
            "target_agent": decision.target_agent,
            "routing_reason": decision.reason,
        },
    }


def character_node(state: AgentState):
    if not state.character_id:
        return {"agent_output": "No character was selected."}

    agent = _get_agent("character")
    request = CharacterRequest(
        character_id=state.character_id,
        story_id=state.story_id,
        branch_id=state.branch_id,
        sequence=state.current_sequence,
        message=state.user_input,
    )
    result = agent.respond(request)
    return {
        "agent_output": result.output,
        "metadata": {
            **state.metadata,
            "character_result": result.metadata,
        },
    }


def narrative_node(state: AgentState):
    agent = _get_agent("narrative")
    request = NarrativeRequest(
        story_id=state.story_id,
        branch_id=state.branch_id,
        sequence=state.current_sequence,
        change=state.user_input,
    )
    result = agent.diverge(request)
    return {
        "agent_output": result.output,
        "metadata": {
            **state.metadata,
            "narrative_result": result.metadata,
        },
    }


def consistency_node(state: AgentState):
    """Validate branch world state if available."""
    from tools.world_state import get_world_state

    branch_id = state.metadata.get("narrative_result", {}).get("branch_id")
    if branch_id:
        ws = get_world_state(state.story_id, branch_id)
        if ws:
            agent = _get_agent("consistency")
            result = agent.validate(ws)
            return {
                "metadata": {
                    **state.metadata,
                    "consistency_checked": True,
                    "consistency_result": result.metadata,
                }
            }

    return {
        "metadata": {
            **state.metadata,
            "consistency_checked": False,
            "consistency_reason": "No branch world state to validate.",
        }
    }


def choose_agent(state: AgentState):
    if state.intent in {"chat", "perspective", "interview"}:
        return "character"
    if state.intent in {"divergence", "expansion", "missing_scene", "crossover"}:
        return "narrative"
    return "character"


# ── Build graph ──────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", route_request)
    graph.add_node("character", character_node)
    graph.add_node("narrative", narrative_node)
    graph.add_node("consistency", consistency_node)

    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router", choose_agent,
        {"character": "character", "narrative": "narrative"},
    )
    graph.add_edge("character", END)
    graph.add_edge("narrative", "consistency")
    graph.add_edge("consistency", END)

    return graph.compile()


reworld_graph = build_graph()