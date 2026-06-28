"""Influence structures and organizational politics modeling.

Maps formal hierarchy alongside informal power networks,
detects gatekeepers, brokers, coalition clusters, and
political vulnerability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from .models import CRMState


@dataclass
class InfluenceReport:
    """Summarized influence analysis for the stakeholder network."""

    pagerank: dict[str, float] = field(default_factory=dict)
    betweenness: dict[str, float] = field(default_factory=dict)
    closeness: dict[str, float] = field(default_factory=dict)
    gatekeepers: list[str] = field(default_factory=list)
    brokers: list[str] = field(default_factory=list)
    coalitions: list[list[str]] = field(default_factory=list)
    isolated: list[str] = field(default_factory=list)
    power_score: dict[str, float] = field(default_factory=dict)
    political_vulnerabilities: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "pagerank": {k: round(v, 4) for k, v in self.pagerank.items()},
            "betweenness": {k: round(v, 4) for k, v in self.betweenness.items()},
            "closeness": {k: round(v, 4) for k, v in self.closeness.items()},
            "gatekeepers": self.gatekeepers,
            "brokers": self.brokers,
            "coalitions": self.coalitions,
            "isolated": self.isolated,
            "power_score": {k: round(v, 4) for k, v in self.power_score.items()},
            "political_vulnerabilities": self.political_vulnerabilities,
        }


TIER_WEIGHT = {
    "c_suite": 1.0,
    "vp": 0.75,
    "director": 0.55,
    "manager": 0.35,
    "individual": 0.15,
    "external": 0.10,
}


def build_influence_graph(state: CRMState) -> nx.DiGraph:
    """Construct a weighted directed graph from relationship data."""
    g = nx.DiGraph()
    for sid, s in state.stakeholders.items():
        g.add_node(sid, label=s.name, tier=s.tier.value, org=s.organization)

    for (src, tgt), rel in state.relationships.items():
        if rel.interaction_count > 0:
            weight = max(0.01, rel.trust_score * (1 + rel.influence_weight))
            g.add_edge(src, tgt, weight=weight, trust=rel.trust_score,
                       influence=rel.influence_weight)
    return g


def analyze_influence(state: CRMState) -> InfluenceReport:
    """Run full influence analysis and return a report."""
    g = build_influence_graph(state)
    report = InfluenceReport()

    if g.number_of_nodes() == 0:
        return report

    # Centrality metrics
    report.pagerank = nx.pagerank(g, weight="weight")
    report.betweenness = nx.betweenness_centrality(g, weight="weight")
    report.closeness = nx.closeness_centrality(g, distance="weight")

    # Gatekeepers: high betweenness, moderate+ pagerank
    betweenness_threshold = 0.1
    for sid, bc in report.betweenness.items():
        if bc > betweenness_threshold and report.pagerank.get(sid, 0) > 0.05:
            report.gatekeepers.append(sid)

    # Brokers: connect otherwise disconnected sub-groups
    undirected = g.to_undirected()
    articulation = list(nx.articulation_points(undirected)) if undirected.number_of_edges() > 0 else []
    report.brokers = [n for n in articulation if n in state.stakeholders]

    # Coalition detection via community finding on undirected graph
    if undirected.number_of_edges() > 0:
        communities = nx.community.greedy_modularity_communities(undirected, weight="weight")
        report.coalitions = [sorted(c) for c in communities if len(c) > 1]

    # Isolated nodes
    report.isolated = [n for n in g.nodes() if g.degree(n) == 0]

    # Composite power score: blend of pagerank, tier, and trust-weighted in-degree
    for sid in state.stakeholders:
        pr = report.pagerank.get(sid, 0)
        tier_w = TIER_WEIGHT.get(state.stakeholders[sid].tier.value, 0.1)
        in_trust = sum(
            state.relationships[(src, sid)].trust_score
            for src in state.stakeholders
            if (src, sid) in state.relationships and state.relationships[(src, sid)].interaction_count > 0
        )
        in_count = max(1, sum(
            1 for src in state.stakeholders
            if (src, sid) in state.relationships and state.relationships[(src, sid)].interaction_count > 0
        ))
        avg_in_trust = in_trust / in_count
        report.power_score[sid] = 0.4 * pr * 10 + 0.3 * tier_w + 0.3 * avg_in_trust

    # Political vulnerabilities
    for sid, s in state.stakeholders.items():
        vulns: list[str] = []
        if report.power_score.get(sid, 0) < 0.2:
            vulns.append("low_influence")
        if sid in report.isolated:
            vulns.append("network_isolation")
        rivals_in_power = [
            r for r in s.rivals
            if report.power_score.get(r, 0) > report.power_score.get(sid, 0)
        ]
        if rivals_in_power:
            vulns.append("outranked_by_rivals")
        allies_present = [a for a in s.allies if a in state.stakeholders]
        if len(allies_present) == 0 and s.tier.value not in ("c_suite",):
            vulns.append("no_allies")
        # Single-dependency: only one strong trust link
        strong_links = [
            r for r in state.get_stakeholder_relationships(sid)
            if r.trust_score > 0.7 and r.interaction_count > 2
        ]
        if len(strong_links) == 1:
            vulns.append("single_dependency")
        if vulns:
            report.political_vulnerabilities[sid] = vulns

    return report
