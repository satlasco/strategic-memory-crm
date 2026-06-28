"""Strategic Memory CRM — Minimal web dashboard.

Run with: python app.py
Then open http://localhost:5000
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template

from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm.entropy import compute_all_entropy, network_entropy
from strategic_memory_crm.graph import build_vis_graph
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.negotiation import build_all_profiles, detect_reciprocal_pairs
from strategic_memory_crm.risk import assess_relationship_risk, full_risk_report
from strategic_memory_crm.trust import compute_trust_trajectory

app = Flask(__name__)

# Generate dataset on startup
STATE = generate_dataset(n_interactions=80, seed=42)


@app.route("/")
def dashboard():
    influence = analyze_influence(STATE)
    entropy_scores = compute_all_entropy(STATE)
    net_entropy = network_entropy(STATE)
    risk_report = full_risk_report(STATE)
    profiles = build_all_profiles(STATE)
    reciprocal = detect_reciprocal_pairs(STATE)

    stakeholders = []
    for sid, s in STATE.stakeholders.items():
        rels = STATE.get_stakeholder_relationships(sid)
        active_rels = [r for r in rels if r.interaction_count > 0]
        avg_trust = (sum(r.trust_score for r in active_rels) / len(active_rels)) if active_rels else 0
        stakeholders.append({
            "id": sid,
            "name": s.name,
            "role": s.role,
            "organization": s.organization,
            "tier": s.tier.value,
            "avg_trust": round(avg_trust, 2),
            "power_score": round(influence.power_score.get(sid, 0), 3),
            "risk_score": round(risk_report[sid].risk_score, 3),
            "risk_factors": risk_report[sid].factors,
            "neg_style": profiles[sid].dominant_style if sid in profiles else "unknown",
            "neg_patterns": profiles[sid].patterns if sid in profiles else [],
            "vulnerabilities": influence.political_vulnerabilities.get(sid, []),
        })

    stakeholders.sort(key=lambda x: x["power_score"], reverse=True)

    return render_template(
        "dashboard.html",
        stakeholders=stakeholders,
        net_entropy=round(net_entropy, 4),
        coalitions=influence.coalitions,
        gatekeepers=[STATE.stakeholders[g].name for g in influence.gatekeepers if g in STATE.stakeholders],
        brokers=[STATE.stakeholders[b].name for b in influence.brokers if b in STATE.stakeholders],
        reciprocal_pairs=[
            {
                "a": STATE.stakeholders[a].name if a in STATE.stakeholders else a,
                "b": STATE.stakeholders[b].name if b in STATE.stakeholders else b,
                "dynamic": label,
            }
            for a, b, label in reciprocal
        ],
        n_interactions=len(STATE.interactions),
        n_relationships=len([r for r in STATE.relationships.values() if r.interaction_count > 0]),
    )


@app.route("/stakeholder/<sid>")
def stakeholder_detail(sid: str):
    s = STATE.stakeholders.get(sid)
    if not s:
        return "Not found", 404

    interactions = STATE.get_stakeholder_interactions(sid)
    interactions.sort(key=lambda i: i.timestamp, reverse=True)

    rels = []
    for r in STATE.get_stakeholder_relationships(sid):
        if r.interaction_count == 0:
            continue
        other_id = r.target_id if r.source_id == sid else r.source_id
        other = STATE.stakeholders.get(other_id)
        if not other:
            continue
        trajectory = compute_trust_trajectory(r)
        rels.append({
            "other_id": other_id,
            "other_name": other.name,
            "trust": round(r.trust_score, 3),
            "entropy": round(r.entropy_score, 3),
            "risk": round(r.risk_level, 3),
            "interactions": r.interaction_count,
            "trajectory": trajectory,
            "reciprocity": round(r.reciprocity_balance, 2),
        })

    rels.sort(key=lambda x: x["trust"], reverse=True)

    influence = analyze_influence(STATE)
    profiles = build_all_profiles(STATE)
    profile = profiles.get(sid)
    risk = full_risk_report(STATE).get(sid)

    return render_template(
        "stakeholder.html",
        s=s,
        relationships=rels,
        interactions=[i.to_dict() for i in interactions[:20]],
        power_score=round(influence.power_score.get(sid, 0), 3),
        pagerank=round(influence.pagerank.get(sid, 0), 4),
        betweenness=round(influence.betweenness.get(sid, 0), 4),
        vulnerabilities=influence.political_vulnerabilities.get(sid, []),
        profile=profile.to_dict() if profile else None,
        risk=risk.to_dict() if risk else None,
    )


@app.route("/graph")
def graph_view():
    return render_template("graph.html")


@app.route("/api/graph")
def api_graph():
    return jsonify(build_vis_graph(STATE))


@app.route("/api/state")
def api_state():
    return jsonify(STATE.to_dict())


@app.route("/api/entropy")
def api_entropy():
    breakdowns = compute_all_entropy(STATE)
    return jsonify({
        "network_entropy": round(network_entropy(STATE), 4),
        "relationships": [b.to_dict() for b in breakdowns],
    })


@app.route("/api/influence")
def api_influence():
    return jsonify(analyze_influence(STATE).to_dict())


@app.route("/api/risk")
def api_risk():
    report = full_risk_report(STATE)
    return jsonify({k: v.to_dict() for k, v in report.items()})


@app.route("/api/negotiations")
def api_negotiations():
    profiles = build_all_profiles(STATE)
    return jsonify({k: v.to_dict() for k, v in profiles.items()})


if __name__ == "__main__":
    print("\n  Strategic Memory CRM")
    print("  ====================")
    print(f"  Loaded {len(STATE.stakeholders)} stakeholders")
    print(f"  Simulated {len(STATE.interactions)} interactions")
    print(f"  Tracked {len([r for r in STATE.relationships.values() if r.interaction_count > 0])} active relationships")
    print(f"  Network entropy: {network_entropy(STATE):.4f}")
    print("\n  Dashboard: http://localhost:5088")
    print("  Graph:     http://localhost:5088/graph")
    print("  API:       http://localhost:5088/api/state\n")
    app.run(debug=True, host="0.0.0.0", port=5088)
