"""Coalition, Faction, and Power Balance Analytics.

Identifies informal power blocs, calculates collective decision influence,
and detects vulnerable bridge nodes (weakest links) in corporate networks.
"""

from __future__ import annotations

from typing import Any

from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import CRMState, OrgTier
from strategic_memory_crm.risk import full_risk_report


def analyze_coalitions_and_power(state: CRMState) -> dict[str, Any]:
    """Extracts formal and informal corporate factions, computes balance of power, and highlights vulnerabilities."""
    inf = analyze_influence(state)
    risk_map = full_risk_report(state)

    total_stakeholders = len(state.stakeholders)
    if total_stakeholders == 0:
        return {"error": "No stakeholders in state"}

    # Total network decision power
    total_decision_power = sum(
        1.0 if s.tier in (OrgTier.C_SUITE, OrgTier.VP) else (0.6 if s.tier == OrgTier.DIRECTOR else 0.3)
        for s in state.stakeholders.values()
    ) or 1.0

    raw_coalitions = inf.coalitions

    faction_list = []
    for idx, c_members in enumerate(raw_coalitions):
        if not c_members:
            continue

        members_detail = []
        faction_decision_power = 0.0
        faction_pagerank_sum = 0.0
        internal_trust_sum = 0.0
        pair_count = 0

        # Calculate metrics for coalition
        for sid in c_members:
            if sid not in state.stakeholders:
                continue
            s = state.stakeholders[sid]
            p_weight = 1.0 if s.tier in (OrgTier.C_SUITE, OrgTier.VP) else (0.6 if s.tier == OrgTier.DIRECTOR else 0.3)
            faction_decision_power += p_weight
            faction_pagerank_sum += inf.pagerank.get(sid, 0.0)

            # Internal trust calculation with peers in same coalition
            for peer_id in c_members:
                if peer_id != sid and peer_id in state.stakeholders:
                    rel = state.relationships.get((sid, peer_id))
                    if rel:
                        internal_trust_sum += rel.trust_score
                        pair_count += 1

            r_obj = risk_map.get(sid)
            members_detail.append({
                "id": sid,
                "name": s.name,
                "role": s.role,
                "organization": s.organization,
                "tier": s.tier.value,
                "pagerank": round(inf.pagerank.get(sid, 0.0), 3),
                "is_gatekeeper": sid in inf.gatekeepers,
                "is_broker": sid in inf.brokers,
                "risk_score": round(r_obj.risk_score, 2) if r_obj else 0.2
            })

        avg_internal_trust = round(internal_trust_sum / max(1, pair_count), 2) if pair_count > 0 else 0.6
        power_share_pct = round((faction_decision_power / total_decision_power) * 100, 1)

        # Identify key leader and weakest link
        members_detail.sort(key=lambda x: x["pagerank"], reverse=True)
        primary_leader = members_detail[0]["name"] if members_detail else "Unknown"

        # Weakest link is member with highest risk score or lowest trust
        weakest_candidate = max(members_detail, key=lambda x: x["risk_score"]) if members_detail else None

        # Determine dominant organization in coalition
        org_counts = {}
        for m in members_detail:
            org = m["organization"]
            org_counts[org] = org_counts.get(org, 0) + 1
        dominant_org = max(org_counts.items(), key=lambda x: x[1])[0] if org_counts else "Cross-Organizational"

        faction_list.append({
            "faction_id": f"faction_{idx + 1}",
            "name": f"{dominant_org} Alliance" if len(org_counts) == 1 else f"Coalition {idx + 1} ({dominant_org} Led)",
            "member_count": len(members_detail),
            "dominant_organization": dominant_org,
            "power_share_percentage": power_share_pct,
            "cumulative_pagerank": round(faction_pagerank_sum, 3),
            "cohesion_internal_trust": avg_internal_trust,
            "primary_leader": primary_leader,
            "weakest_link": {
                "name": weakest_candidate["name"],
                "role": weakest_candidate["role"],
                "risk_score": weakest_candidate["risk_score"]
            } if weakest_candidate else None,
            "members": members_detail
        })

    faction_list.sort(key=lambda x: x["power_share_percentage"], reverse=True)

    return {
        "total_factions": len(faction_list),
        "total_stakeholders": total_stakeholders,
        "balance_of_power": faction_list,
        "key_gatekeepers": [
            {"id": sid, "name": state.stakeholders[sid].name, "role": state.stakeholders[sid].role}
            for sid in inf.gatekeepers if sid in state.stakeholders
        ],
        "key_brokers": [
            {"id": sid, "name": state.stakeholders[sid].name, "role": state.stakeholders[sid].role}
            for sid in inf.brokers if sid in state.stakeholders
        ]
    }
