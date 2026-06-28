"""Relationship risk assessment.

Combines trust trajectory, entropy, political vulnerability,
and dependency concentration into a per-relationship and
per-stakeholder risk score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CRMState

from .entropy import compute_entropy
from .influence import analyze_influence
from .trust import compute_trust_trajectory


@dataclass
class RiskAssessment:
    """Risk profile for a stakeholder or relationship."""

    entity_id: str = ""
    risk_score: float = 0.0
    factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "risk_score": round(self.risk_score, 3),
            "factors": self.factors,
            "recommendations": self.recommendations,
        }


def assess_relationship_risk(state: CRMState, src: str, tgt: str) -> RiskAssessment:
    """Evaluate risk for a specific directed relationship."""
    key = (src, tgt)
    rel = state.relationships.get(key)
    if rel is None or rel.interaction_count == 0:
        return RiskAssessment(entity_id=f"{src}->{tgt}", risk_score=0.5,
                              factors=["no_interaction_history"])

    assessment = RiskAssessment(entity_id=f"{src}->{tgt}")
    risk = 0.0

    # Trust level
    if rel.trust_score < 0.3:
        risk += 0.25
        assessment.factors.append("low_trust")
        assessment.recommendations.append("Prioritize trust-building interactions")
    elif rel.trust_score < 0.5:
        risk += 0.10
        assessment.factors.append("below_average_trust")

    # Trust trajectory
    trajectory = compute_trust_trajectory(rel)
    if trajectory == "deteriorating":
        risk += 0.20
        assessment.factors.append("deteriorating_trust")
        assessment.recommendations.append("Investigate root cause of declining trust")

    # Entropy
    entropy_bd = compute_entropy(rel, state)
    if entropy_bd.risk_label == "volatile":
        risk += 0.25
        assessment.factors.append("volatile_relationship")
        assessment.recommendations.append("Increase interaction regularity to stabilize")
    elif entropy_bd.risk_label == "uncertain":
        risk += 0.10
        assessment.factors.append("uncertain_dynamics")

    # Reciprocity imbalance
    if abs(rel.reciprocity_balance) > 0.5:
        risk += 0.10
        assessment.factors.append("reciprocity_imbalance")
        assessment.recommendations.append("Re-balance give-and-take dynamics")

    # Low interaction frequency
    if rel.interaction_count < 3:
        risk += 0.10
        assessment.factors.append("thin_relationship")
        assessment.recommendations.append("Increase engagement frequency")

    assessment.risk_score = min(1.0, risk)
    rel.risk_level = assessment.risk_score
    return assessment


def assess_stakeholder_risk(state: CRMState, stakeholder_id: str) -> RiskAssessment:
    """Evaluate aggregate relationship risk for a stakeholder."""
    assessment = RiskAssessment(entity_id=stakeholder_id)
    rels = state.get_stakeholder_relationships(stakeholder_id)
    if not rels:
        assessment.risk_score = 0.5
        assessment.factors.append("no_relationships")
        return assessment

    active_rels = [r for r in rels if r.interaction_count > 0]
    if not active_rels:
        assessment.risk_score = 0.4
        assessment.factors.append("no_active_relationships")
        return assessment

    # Average relationship risk
    rel_risks: list[float] = []
    for r in active_rels:
        other = r.target_id if r.source_id == stakeholder_id else r.source_id
        ra = assess_relationship_risk(state, r.source_id, r.target_id)
        rel_risks.append(ra.risk_score)

    avg_risk = sum(rel_risks) / len(rel_risks)

    # Concentration risk: how dependent on a single relationship
    if len(active_rels) == 1:
        avg_risk += 0.15
        assessment.factors.append("single_relationship_dependency")
        assessment.recommendations.append("Diversify relationship portfolio")
    elif len(active_rels) == 2:
        avg_risk += 0.05
        assessment.factors.append("narrow_network")

    # Political vulnerability from influence analysis
    influence_report = analyze_influence(state)
    vulns = influence_report.political_vulnerabilities.get(stakeholder_id, [])
    for v in vulns:
        if v == "outranked_by_rivals":
            avg_risk += 0.10
            assessment.factors.append("outranked_by_rivals")
        elif v == "no_allies":
            avg_risk += 0.08
            assessment.factors.append("no_allies_in_network")
            assessment.recommendations.append("Build strategic alliances")
        elif v == "network_isolation":
            avg_risk += 0.15
            assessment.factors.append("isolated_in_network")
            assessment.recommendations.append("Increase network engagement")

    assessment.risk_score = min(1.0, avg_risk)
    return assessment


def full_risk_report(state: CRMState) -> dict[str, RiskAssessment]:
    """Generate risk assessments for all stakeholders."""
    return {
        sid: assess_stakeholder_risk(state, sid)
        for sid in state.stakeholders
    }
