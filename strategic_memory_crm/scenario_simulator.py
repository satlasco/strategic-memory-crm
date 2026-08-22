"""What-If Predictive Scenario Simulator for Strategic Memory CRM.

Enables risk-free modeling of hypothetical stakeholder moves, broken commitments,
conflicts, strategic favors, or temporal relationship decay before execution.
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Any, Optional

from strategic_memory_crm.entropy import network_entropy
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    Sentiment,
    Stakeholder,
)
from strategic_memory_crm.risk import full_risk_report
from strategic_memory_crm.trust import apply_interaction, passive_decay


def simulate_what_if(
    state: CRMState,
    scenario_type: str,
    source_id: str,
    target_id: Optional[str] = None,
    severity: float = 1.0,
    time_lapse_days: int = 0,
    description: str = ""
) -> dict[str, Any]:
    """Runs a hypothetical what-if scenario on a clone of the CRMState and returns the projected impact delta.

    Scenario Types:
        - "conflict": Open confrontation or disagreement between source and target.
        - "broken_commitment": Source fails to deliver on a promise to target.
        - "kept_commitment": Source successfully delivers a high-value commitment.
        - "strategic_favor": Source does a major unreciprocated favor for target.
        - "betrayal": Catastrophic breach of trust between source and target.
        - "passive_decay": Simulates relationship decay after N days of no contact.
    """
    # Helper to resolve IDs
    def resolve_sid(val: Optional[str]) -> Optional[str]:
        if not val:
            return None
        if val in state.stakeholders:
            return val
        val_lower = val.strip().lower()
        for sid, s in state.stakeholders.items():
            if s.name.strip().lower() == val_lower:
                return sid
        return None

    sid1 = resolve_sid(source_id)
    sid2 = resolve_sid(target_id) if target_id else None

    if not sid1 or sid1 not in state.stakeholders:
        return {"error": f"Source stakeholder '{source_id}' could not be resolved."}

    # Clone state into isolated sandbox
    sandbox_state: CRMState = copy.deepcopy(state)

    # 1. Capture baseline metrics
    baseline_entropy = network_entropy(state)
    baseline_risks = {sid: r.risk_score for sid, r in full_risk_report(state).items()}
    baseline_trusts = {
        k: r.trust_score for k, r in state.relationships.items()
    }
    baseline_influence = analyze_influence(state).pagerank

    # 2. Apply hypothetical scenario
    scenario_type_clean = scenario_type.lower().strip()
    simulated_events = []

    if scenario_type_clean == "passive_decay" or time_lapse_days > 0:
        days = time_lapse_days if time_lapse_days > 0 else int(30 * severity)
        for rel in sandbox_state.relationships.values():
            passive_decay(rel, days)
        simulated_events.append(f"Simulated {days} days of passive temporal relationship decay across {len(sandbox_state.relationships)} relationships.")

    if sid2 and sid2 in sandbox_state.stakeholders:
        s1 = sandbox_state.stakeholders[sid1]
        s2 = sandbox_state.stakeholders[sid2]
        rel1 = sandbox_state.get_or_create_relationship(sid1, sid2)
        rel2 = sandbox_state.get_or_create_relationship(sid2, sid1)

        itype = InteractionType.MEETING
        sentiment = Sentiment.NEUTRAL
        commitments_kept = None
        concession = False
        power_move = False

        if scenario_type_clean == "conflict":
            itype = InteractionType.CONFLICT
            sentiment = Sentiment.VERY_NEGATIVE if severity > 1.2 else Sentiment.NEGATIVE
            power_move = True
        elif scenario_type_clean == "broken_commitment":
            itype = InteractionType.NEGOTIATION
            sentiment = Sentiment.NEGATIVE
            commitments_kept = False
        elif scenario_type_clean == "kept_commitment":
            itype = InteractionType.MEETING
            sentiment = Sentiment.POSITIVE
            commitments_kept = True
        elif scenario_type_clean == "strategic_favor":
            itype = InteractionType.FAVOR
            sentiment = Sentiment.VERY_POSITIVE if severity > 1.2 else Sentiment.POSITIVE
            concession = True
        elif scenario_type_clean == "betrayal":
            itype = InteractionType.BETRAYAL
            sentiment = Sentiment.VERY_NEGATIVE
            commitments_kept = False
            power_move = True

        hypothetical_interaction = Interaction(
            id=f"sim_{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now().isoformat()[:10],
            type=itype,
            participants=[sid1, sid2],
            initiator=sid1,
            sentiment=sentiment,
            trust_delta=0.0,
            summary=description or f"Simulated {scenario_type_clean} scenario",
            commitments_made=["Hypothetical Commitment"] if commitments_kept is not None else [],
            commitments_kept=commitments_kept,
            concession_made=concession,
            power_move=power_move
        )

        sandbox_state.add_interaction(hypothetical_interaction)
        apply_interaction(rel1, hypothetical_interaction, s1, s2)
        apply_interaction(rel2, hypothetical_interaction, s2, s1)
        simulated_events.append(f"Applied hypothetical {scenario_type_clean} between {s1.name} and {s2.name}.")

    # 3. Calculate post-simulation metrics
    post_entropy = network_entropy(sandbox_state)
    post_risks = {sid: r.risk_score for sid, r in full_risk_report(sandbox_state).items()}
    post_influence = analyze_influence(sandbox_state).pagerank

    # 4. Compute Deltas & Shifts
    entropy_delta = round(post_entropy - baseline_entropy, 3)

    # Shift in risk for primary stakeholders
    risk_shifts = []
    for sid, base_r in baseline_risks.items():
        curr_r = post_risks.get(sid, base_r)
        diff = round(curr_r - base_r, 3)
        if abs(diff) >= 0.01:
            risk_shifts.append({
                "stakeholder_id": sid,
                "stakeholder_name": state.stakeholders[sid].name,
                "baseline_risk": round(base_r, 2),
                "simulated_risk": round(curr_r, 2),
                "delta": diff,
                "direction": "increased" if diff > 0 else "decreased"
            })
    risk_shifts.sort(key=lambda x: abs(x["delta"]), reverse=True)

    # Shift in trust for affected pairs
    trust_shifts = []
    for k, base_t in baseline_trusts.items():
        curr_t = sandbox_state.relationships[k].trust_score if k in sandbox_state.relationships else base_t
        diff = round(curr_t - base_t, 3)
        if abs(diff) >= 0.01:
            s_from = state.stakeholders.get(k[0])
            s_to = state.stakeholders.get(k[1])
            trust_shifts.append({
                "from_name": s_from.name if s_from else k[0],
                "to_name": s_to.name if s_to else k[1],
                "baseline_trust": round(base_t, 2),
                "simulated_trust": round(curr_t, 2),
                "delta": diff
            })
    trust_shifts.sort(key=lambda x: abs(x["delta"]), reverse=True)

    # Second-degree contagion analysis
    contagion_nodes = []
    if sid1 and sid2:
        # Stakeholders connected to target or source who might react
        allies_1 = set(state.stakeholders[sid1].allies)
        allies_2 = set(state.stakeholders[sid2].allies)
        shared_peers = allies_1.union(allies_2)
        for peer_id in shared_peers:
            if peer_id in state.stakeholders and peer_id not in (sid1, sid2):
                p_obj = state.stakeholders[peer_id]
                contagion_nodes.append({
                    "id": peer_id,
                    "name": p_obj.name,
                    "role": p_obj.role,
                    "political_risk": "High Exposure" if p_obj.personality.get("political_savvy", 0.5) > 0.6 else "Moderate"
                })

    # Tactical mitigation advice based on outcome
    mitigations = []
    if entropy_delta > 0.05:
        mitigations.append("Network volatility increases significantly; schedule bilateral damage-control meetings with key bridge brokers.")
    if scenario_type_clean in ("conflict", "broken_commitment", "betrayal"):
        mitigations.append("Prepare compensatory value offerings early to prevent negative reciprocity cascading across mutual allies.")
    elif scenario_type_clean == "strategic_favor":
        mitigations.append("Leverage newly earned reciprocity window within 14 days before passive decay diminishes goodwill.")
    elif scenario_type_clean == "passive_decay":
        mitigations.append("Re-engage high-PageRank stakeholders with low-friction touchpoints to restore baseline trust.")

    return {
        "status": "success",
        "scenario": {
            "type": scenario_type_clean,
            "source_name": state.stakeholders[sid1].name,
            "target_name": state.stakeholders[sid2].name if sid2 and sid2 in state.stakeholders else "Network-wide",
            "severity": severity,
            "simulated_events": simulated_events
        },
        "impact_summary": {
            "baseline_entropy": round(baseline_entropy, 3),
            "simulated_entropy": round(post_entropy, 3),
            "entropy_delta": entropy_delta,
            "stability_status": "Destabilizing (High Risk)" if entropy_delta > 0.05 else ("Stabilizing" if entropy_delta < -0.05 else "Neutral")
        },
        "risk_shifts": risk_shifts,
        "trust_shifts": trust_shifts,
        "contagion_exposure": contagion_nodes,
        "strategic_mitigations": mitigations
    }
