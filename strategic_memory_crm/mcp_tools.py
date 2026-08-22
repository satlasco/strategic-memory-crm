"""MCP Tool implementations for Strategic Memory CRM.

Provides structured behavioral intelligence and graph analytics tools
for LLMs via the Model Context Protocol (MCP).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Optional

from strategic_memory_crm.entropy import compute_entropy, network_entropy
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    OrgTier,
    Sentiment,
    Stakeholder,
)
from strategic_memory_crm.negotiation import build_all_profiles, build_negotiation_profile
from strategic_memory_crm.risk import assess_relationship_risk, full_risk_report
from strategic_memory_crm.trust import apply_interaction, compute_trust_trajectory


def _resolve_sid(state: CRMState, val: str) -> Optional[str]:
    """Resolves stakeholder ID from either ID or exact/case-insensitive name."""
    if not val:
        return None
    if val in state.stakeholders:
        return val
    val_lower = val.strip().lower()
    for sid, s in state.stakeholders.items():
        if s.name.strip().lower() == val_lower:
            return sid
    return None


def list_stakeholders(state: CRMState) -> list[dict[str, Any]]:
    """Returns a list of all stakeholders with behavioral summary and risk rating."""
    risk_map = full_risk_report(state)
    profiles = build_all_profiles(state)

    results = []
    for sid, s in state.stakeholders.items():
        r = risk_map.get(sid)
        p = profiles.get(sid)
        results.append({
            "id": sid,
            "name": s.name,
            "role": s.role,
            "organization": s.organization,
            "tier": s.tier.value,
            "dominant_style": p.dominant_style if p else "collaborative",
            "reliability_score": round(p.reliability_score, 2) if p else 0.8,
            "risk_score": round(r.risk_score, 2) if r else 0.2,
            "risk_level": "High" if r and r.risk_score > 0.5 else ("Moderate" if r and r.risk_score > 0.3 else "Low"),
            "goals": s.goals,
            "vulnerabilities": s.vulnerabilities,
            "allies": [state.stakeholders[a].name for a in s.allies if a in state.stakeholders],
            "rivals": [state.stakeholders[rv].name for rv in s.rivals if rv in state.stakeholders]
        })
    return results


def get_stakeholder_intel(state: CRMState, stakeholder_id: str) -> dict[str, Any]:
    """Retrieves deep behavioral intelligence, trust ties, negotiation stance, and risk breakdown for a stakeholder."""
    sid = _resolve_sid(state, stakeholder_id)
    if not sid or sid not in state.stakeholders:
        return {"error": f"Stakeholder '{stakeholder_id}' not found."}

    s = state.stakeholders[sid]
    profile = build_negotiation_profile(state, sid)
    risk_map = full_risk_report(state)
    risk = risk_map.get(sid)

    # Relationships and trust scores
    rels_info = []
    for r in state.get_stakeholder_relationships(sid):
        if r.interaction_count > 0:
            other_id = r.target_id if r.source_id == sid else r.source_id
            other = state.stakeholders.get(other_id)
            if other:
                rels_info.append({
                    "peer_id": other_id,
                    "peer_name": other.name,
                    "peer_role": other.role,
                    "peer_organization": other.organization,
                    "trust_score": round(r.trust_score, 2),
                    "interaction_count": r.interaction_count,
                    "reciprocity_balance": round(r.reciprocity_balance, 2),
                    "sentiment_history_avg": round(sum(r.sentiment_history) / max(1, len(r.sentiment_history)), 2) if r.sentiment_history else 0.0,
                    "risk_level": round(r.risk_level, 2)
                })
    rels_info.sort(key=lambda x: x["trust_score"], reverse=True)

    # Recent interactions
    interactions = [
        {
            "id": i.id,
            "type": i.type.value,
            "timestamp": i.timestamp,
            "sentiment": i.sentiment.name.lower(),
            "summary": i.summary,
            "context": i.context,
            "commitments_made": i.commitments_made,
            "commitments_kept": i.commitments_kept,
            "concession_made": i.concession_made,
            "power_move": i.power_move
        }
        for i in state.get_stakeholder_interactions(sid)[-6:]
    ]

    return {
        "stakeholder": {
            "id": sid,
            "name": s.name,
            "role": s.role,
            "organization": s.organization,
            "tier": s.tier.value,
            "personality": {k: round(v, 2) for k, v in s.personality.items()},
            "goals": s.goals,
            "vulnerabilities": s.vulnerabilities,
            "allies": [state.stakeholders[a].name for a in s.allies if a in state.stakeholders],
            "rivals": [state.stakeholders[rv].name for rv in s.rivals if rv in state.stakeholders]
        },
        "negotiation_profile": {
            "dominant_style": profile.dominant_style,
            "total_negotiations": profile.total_negotiations,
            "concessions_made": profile.concessions_made,
            "concessions_received": profile.concessions_received,
            "commitments_kept_ratio": f"{profile.commitments_kept}/{profile.commitments_made}" if profile.commitments_made > 0 else "N/A",
            "reliability_score": round(profile.reliability_score, 2),
            "behavioral_patterns": profile.patterns,
        },
        "risk_assessment": {
            "risk_score": round(risk.risk_score, 2) if risk else 0.2,
            "factors": risk.factors if risk else [],
            "recommendations": risk.recommendations if risk else []
        },
        "key_relationships": rels_info,
        "recent_interactions": interactions
    }


def get_organization_politics(state: CRMState) -> dict[str, Any]:
    """Analyzes the informal power structure, key influencers, gatekeepers, brokers, and network entropy."""
    inf = analyze_influence(state)
    net_ent = network_entropy(state)

    def name_map(d: dict[str, float], top_n: int = 5):
        sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [
            {
                "id": sid,
                "name": state.stakeholders[sid].name if sid in state.stakeholders else sid,
                "role": state.stakeholders[sid].role if sid in state.stakeholders else "",
                "organization": state.stakeholders[sid].organization if sid in state.stakeholders else "",
                "score": round(val, 3)
            }
            for sid, val in sorted_items
        ]

    gatekeepers = [
        {
            "id": sid,
            "name": state.stakeholders[sid].name if sid in state.stakeholders else sid,
            "role": state.stakeholders[sid].role if sid in state.stakeholders else "",
            "organization": state.stakeholders[sid].organization if sid in state.stakeholders else ""
        }
        for sid in inf.gatekeepers if sid in state.stakeholders
    ]

    brokers = [
        {
            "id": sid,
            "name": state.stakeholders[sid].name if sid in state.stakeholders else sid,
            "role": state.stakeholders[sid].role if sid in state.stakeholders else "",
            "organization": state.stakeholders[sid].organization if sid in state.stakeholders else ""
        }
        for sid in inf.brokers if sid in state.stakeholders
    ]

    coalitions = [
        [
            state.stakeholders[sid].name if sid in state.stakeholders else sid
            for sid in c
        ]
        for c in inf.coalitions if len(c) > 1
    ]

    return {
        "network_overview": {
            "total_stakeholders": len(state.stakeholders),
            "total_relationships": len(state.relationships),
            "total_interactions": len(state.interactions),
            "network_entropy": round(net_ent, 3),
            "network_stability": "Volatile / High Entropy" if net_ent > 0.6 else ("Moderate" if net_ent > 0.3 else "Stable / Predictable")
        },
        "informal_influencers_pagerank": name_map(inf.pagerank, top_n=5),
        "information_bridges_betweenness": name_map(inf.betweenness, top_n=5),
        "gatekeepers": gatekeepers,
        "brokers_articulation_points": brokers,
        "detected_coalitions": coalitions
    }


def analyze_relationship(state: CRMState, source_id: str, target_id: str) -> dict[str, Any]:
    """Deep behavioral dive into the dyadic relationship between two stakeholders."""
    sid1 = _resolve_sid(state, source_id)
    sid2 = _resolve_sid(state, target_id)

    if not sid1 or not sid2 or sid1 not in state.stakeholders or sid2 not in state.stakeholders:
        return {"error": f"Could not resolve stakeholders '{source_id}' and/or '{target_id}'."}

    s1 = state.stakeholders[sid1]
    s2 = state.stakeholders[sid2]

    rel = state.get_or_create_relationship(sid1, sid2)
    traj = compute_trust_trajectory(rel)
    ent_breakdown = compute_entropy(rel, state)
    ent = ent_breakdown.composite_entropy
    r_risk = assess_relationship_risk(state, sid1, sid2)

    # Interpersonal interactions
    inter_list = [
        {
            "id": i.id,
            "type": i.type.value,
            "initiator": state.stakeholders[i.initiator].name if i.initiator in state.stakeholders else i.initiator,
            "timestamp": i.timestamp,
            "sentiment": i.sentiment.name.lower(),
            "summary": i.summary,
            "concession_made": i.concession_made,
            "commitments_kept": i.commitments_kept
        }
        for i in state.interactions
        if sid1 in i.participants and sid2 in i.participants
    ]

    return {
        "source_stakeholder": {"id": sid1, "name": s1.name, "role": s1.role, "organization": s1.organization},
        "target_stakeholder": {"id": sid2, "name": s2.name, "role": s2.role, "organization": s2.organization},
        "trust_score": round(rel.trust_score, 2),
        "trust_trajectory": traj,
        "relationship_entropy": round(ent, 3),
        "relationship_risk": {
            "score": round(r_risk.risk_score, 2),
            "factors": r_risk.factors,
            "recommendations": r_risk.recommendations
        },
        "dynamics": {
            "interaction_count": rel.interaction_count,
            "reciprocity_balance": round(rel.reciprocity_balance, 2),
            "sentiment_history_avg": round(sum(rel.sentiment_history) / max(1, len(rel.sentiment_history)), 2) if rel.sentiment_history else 0.0,
            "risk_level": round(rel.risk_level, 2)
        },
        "shared_interactions": inter_list
    }


def log_interaction(
    state: CRMState,
    source_id: str,
    target_id: str,
    interaction_type: str = "meeting",
    summary: str = "",
    context: str = "",
    sentiment: str = "neutral",
    commitments_made: Optional[list[str]] = None,
    commitments_kept: Optional[bool] = None,
    concession_made: bool = False,
    power_move: bool = False
) -> dict[str, Any]:
    """Logs a new interaction between stakeholders and updates relationship trust dynamically."""
    sid1 = _resolve_sid(state, source_id)
    sid2 = _resolve_sid(state, target_id)

    if not sid1 or not sid2 or sid1 not in state.stakeholders or sid2 not in state.stakeholders:
        return {"error": f"Invalid source '{source_id}' or target '{target_id}'."}

    # Normalize type
    try:
        itype = InteractionType(interaction_type.lower().strip())
    except ValueError:
        itype = InteractionType.MEETING

    # Normalize sentiment
    sentiment_map = {
        "very_positive": Sentiment.VERY_POSITIVE,
        "positive": Sentiment.POSITIVE,
        "neutral": Sentiment.NEUTRAL,
        "negative": Sentiment.NEGATIVE,
        "very_negative": Sentiment.VERY_NEGATIVE,
    }
    sent = sentiment_map.get(sentiment.lower().strip(), Sentiment.NEUTRAL)

    interaction = Interaction(
        id=uuid.uuid4().hex[:8],
        timestamp=datetime.now().isoformat()[:10],
        type=itype,
        participants=[sid1, sid2],
        initiator=sid1,
        sentiment=sent,
        trust_delta=0.0,
        summary=summary,
        context=context,
        commitments_made=commitments_made or [],
        commitments_kept=commitments_kept,
        concession_made=concession_made,
        power_move=power_move
    )

    state.add_interaction(interaction)

    # Apply to directional relationships
    s1 = state.stakeholders[sid1]
    s2 = state.stakeholders[sid2]
    rel1 = state.get_or_create_relationship(sid1, sid2)
    rel2 = state.get_or_create_relationship(sid2, sid1)

    apply_interaction(rel1, interaction, s1, s2)
    apply_interaction(rel2, interaction, s2, s1)

    return {
        "status": "success",
        "message": f"Interaction logged between {s1.name} and {s2.name}.",
        "interaction_id": interaction.id,
        "updated_trust_score": round(rel1.trust_score, 2),
        "updated_interaction_count": rel1.interaction_count
    }


def add_stakeholder(
    state: CRMState,
    name: str,
    role: str,
    organization: str,
    org_tier: str = "individual",
    personality: Optional[dict[str, float]] = None,
    goals: Optional[list[str]] = None,
    vulnerabilities: Optional[list[str]] = None,
    allies: Optional[list[str]] = None,
    rivals: Optional[list[str]] = None
) -> dict[str, Any]:
    """Adds a new stakeholder to the strategic memory database."""
    sid = name.lower().replace(" ", "_")
    if sid in state.stakeholders:
        sid = f"{sid}_{uuid.uuid4().hex[:4]}"

    tier_map = {
        "c_suite": OrgTier.C_SUITE,
        "vp": OrgTier.VP,
        "director": OrgTier.DIRECTOR,
        "manager": OrgTier.MANAGER,
        "individual": OrgTier.INDIVIDUAL,
        "external": OrgTier.EXTERNAL,
    }
    tier = tier_map.get(org_tier.lower().strip(), OrgTier.INDIVIDUAL)

    default_personality = {
        "assertiveness": 0.5,
        "openness": 0.5,
        "agreeableness": 0.5,
        "conscientiousness": 0.5,
        "political_savvy": 0.5
    }
    if personality:
        default_personality.update(personality)

    stakeholder = Stakeholder(
        id=sid,
        name=name,
        role=role,
        organization=organization,
        tier=tier,
        personality=default_personality,
        goals=goals or [],
        vulnerabilities=vulnerabilities or [],
        allies=allies or [],
        rivals=rivals or []
    )

    state.add_stakeholder(stakeholder)

    return {
        "status": "success",
        "message": f"Stakeholder '{name}' successfully created.",
        "stakeholder_id": sid
    }


def generate_tactical_briefing(state: CRMState, stakeholder_id: str, meeting_objective: str = "") -> dict[str, Any]:
    """Generates an executive-level pre-meeting tactical battleplan, psychological leverage analysis, and dos/don'ts."""
    sid = _resolve_sid(state, stakeholder_id)
    if not sid or sid not in state.stakeholders:
        return {"error": f"Stakeholder '{stakeholder_id}' not found."}

    s = state.stakeholders[sid]
    profile = build_negotiation_profile(state, sid)
    risk_map = full_risk_report(state)
    risk = risk_map.get(sid)

    rels = []
    for r in state.get_stakeholder_relationships(sid):
        if r.interaction_count > 0:
            other_id = r.target_id if r.source_id == sid else r.source_id
            other = state.stakeholders.get(other_id)
            if other:
                rels.append({"other_name": other.name, "trust": round(r.trust_score, 2)})
    rels.sort(key=lambda x: x["trust"], reverse=True)

    dom_style = profile.dominant_style if profile else "collaborative"
    rel_score = profile.reliability_score if profile else 0.8
    risk_score = risk.risk_score if risk else 0.3
    allies_text = ", ".join([f"{r['other_name']} (Trust: {r['trust']})" for r in rels[:3]]) or "None established"

    briefing_markdown = f"""# 🎯 Executive Strategic Briefing: {s.name}
**Role:** {s.role} — {s.organization} ({s.tier.value.upper()})
**Meeting Objective:** {meeting_objective or 'Strategic Alignment & Deal Negotiation'}

---

### 1. 🧠 Psychological Profile & Negotiation Stance
* **Dominant Negotiation Style:** `{dom_style.upper()}` (Reliability Score: {rel_score*100:.0f}%)
* **Psychometric Tendencies:**
  * Assertiveness: {s.personality.get('assertiveness', 0.5)*100:.0f}%
  * Political Savvy: {s.personality.get('political_savvy', 0.5)*100:.0f}%
  * Agreeableness: {s.personality.get('agreeableness', 0.5)*100:.0f}%
  * Conscientiousness: {s.personality.get('conscientiousness', 0.5)*100:.0f}%
* **Strongest Network Ties:** {allies_text}

---

### 2. ⚠️ Risk Assessment & Vulnerabilities
* **Composite Relationship Risk:** `{risk_score:.2f}` ({'High Risk' if risk_score > 0.5 else 'Moderate' if risk_score > 0.3 else 'Healthy'})
* **Core Drivers & Goals:** {', '.join(s.goals) if s.goals else 'Maintaining divisional standing and operational autonomy.'}
* **Known Vulnerabilities:** {', '.join(s.vulnerabilities) if s.vulnerabilities else 'Sensitive to status challenges and external timeline pressure.'}

---

### 3. ⚔️ Tactical Playbook & Leverage Points
* **Opening Strategy:** {'Acknowledge authority and present high-level governance structure.' if dom_style in ['dominator', 'competitor'] else 'Lead with shared milestones and collaborative wins.'}
* **Concession Strategy:** {'Never give an unreciprocated concession; hold ground on key governance items.' if dom_style == 'dominator' else 'Exchange low-cost concessions early to build reciprocity.'}
* **Leverage Anchor:** Anchor proposals to their stated goal ({s.goals[0] if s.goals else 'organizational excellence'}).

---

### 4. 🚫 Critical Pitfalls to Avoid
* ❌ Do not corner them in open plenary sessions if political savvy is high.
* ❌ Avoid vague timelines — anchor all commitments to measurable dates.
"""

    return {
        "stakeholder_id": sid,
        "stakeholder_name": s.name,
        "briefing": briefing_markdown,
        "key_metrics": {
            "dominant_style": dom_style,
            "reliability_score": round(rel_score, 2),
            "risk_score": round(risk_score, 2)
        }
    }
