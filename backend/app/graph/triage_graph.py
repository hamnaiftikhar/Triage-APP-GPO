from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.models.triage_state import TriageCategory, TriageState
from app.services.classifier import classify_text


def classifier_node(state: TriageState) -> dict:
    classification = classify_text(state.raw_text)
    return {
        "category": classification.category,
        "urgency": classification.urgency,
        "status": state.status,
    }


def router_node(state: TriageState) -> dict:
    category = state.category
    queue_name = "Clinical Queue" if category == TriageCategory.clinical else "Operations Queue"
    return {"queue_name": queue_name}


def build_triage_graph():
    graph = StateGraph(TriageState)
    graph.add_node("classifier_node", classifier_node)
    graph.add_node("router_node", router_node)
    graph.add_edge(START, "classifier_node")
    graph.add_edge("classifier_node", "router_node")
    graph.add_edge("router_node", END)
    return graph.compile()
