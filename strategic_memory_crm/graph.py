"""Stakeholder graph construction and serialization for visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from .models import CRMState

from .influence import TIER_WEIGHT, build_influence_graph


def build_vis_graph(state: CRMState) -> dict:
    """Build a JSON-serializable graph for front-end rendering.

    Returns a dict with 'nodes' and 'edges' arrays compatible with
    D3.js / vis.js / Cytoscape.js force-directed layouts.
    """
    g = build_influence_graph(state)
    pr = nx.pagerank(g, weight="weight") if g.number_of_nodes() > 0 else {}

    nodes = []
    for sid, s in state.stakeholders.items():
        node = {
            "id": sid,
            "label": s.name,
            "role": s.role,
            "organization": s.organization,
            "tier": s.tier.value,
            "size": 10 + pr.get(sid, 0) * 200,
            "color": _org_color(s.organization),
            "power": round(pr.get(sid, 0) * 100, 1),
        }
        nodes.append(node)

    edges = []
    for (src, tgt), rel in state.relationships.items():
        if rel.interaction_count == 0:
            continue
        edge = {
            "source": src,
            "target": tgt,
            "trust": round(rel.trust_score, 2),
            "weight": rel.interaction_count,
            "entropy": round(rel.entropy_score, 2),
            "risk": round(rel.risk_level, 2),
            "color": _trust_color(rel.trust_score),
            "width": max(1, min(8, rel.interaction_count)),
            "style": "dashed" if rel.trust_score < 0.3 else "solid",
        }
        edges.append(edge)

    return {"nodes": nodes, "edges": edges}


_ORG_COLORS = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
    "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
]
_org_map: dict[str, str] = {}


def _org_color(org: str) -> str:
    if org not in _org_map:
        _org_map[org] = _ORG_COLORS[len(_org_map) % len(_ORG_COLORS)]
    return _org_map[org]


def _trust_color(trust: float) -> str:
    if trust >= 0.7:
        return "#2ca02c"
    if trust >= 0.4:
        return "#ff7f0e"
    return "#d62728"
