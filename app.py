"""Strategic Memory CRM — Behavioral Intelligence & Relationship Risk Platform.

Run with: python app.py
Then open http://localhost:5088
"""

from __future__ import annotations

import io
import json
import socket
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure UTF-8 output on Windows consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, jsonify, render_template, request

from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm.entropy import compute_all_entropy, network_entropy
from strategic_memory_crm.graph import build_vis_graph
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    OrgTier,
    Sentiment,
    Stakeholder,
)
from strategic_memory_crm.negotiation import build_all_profiles, detect_reciprocal_pairs
from strategic_memory_crm.risk import assess_relationship_risk, full_risk_report
from strategic_memory_crm.storage import load_state_from_file, save_state_to_file
from strategic_memory_crm.trust import apply_interaction, compute_trust_trajectory

app = Flask(__name__)

# Data storage path
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "crm_state.json"

# Load persistent state or generate default baseline
STATE: CRMState = load_state_from_file(DATA_FILE)
if STATE is None or len(STATE.stakeholders) == 0:
    STATE = generate_dataset(n_interactions=80, seed=42)
    save_state_to_file(STATE, DATA_FILE)


def is_port_in_use(port: int) -> bool:
    """Check if port is currently occupied on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False


def find_free_port(start_port: int = 5088, max_tries: int = 50) -> int:
    """Find the next available port starting from `start_port`."""
    for port in range(start_port, start_port + max_tries):
        if not is_port_in_use(port):
            return port
    return start_port


# --- Views ---------------------------------------------------------------

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
            "risk_score": round(risk_report[sid].risk_score, 3) if sid in risk_report else 0.0,
            "risk_factors": risk_report[sid].factors if sid in risk_report else [],
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
        return "Stakeholder not found", 404

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
        interactions=[i.to_dict() for i in interactions[:30]],
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


# --- REST APIs -----------------------------------------------------------

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


@app.route("/api/stakeholder", methods=["POST"])
def api_create_stakeholder():
    """Create and persist a new stakeholder."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Stakeholder name is required"}), 400

    role = data.get("role", "").strip()
    org = data.get("organization", "").strip()
    tier_str = data.get("tier", "individual").strip().lower()
    try:
        tier = OrgTier(tier_str)
    except ValueError:
        tier = OrgTier.INDIVIDUAL

    sid = data.get("id") or uuid.uuid4().hex[:8]
    personality = data.get("personality", {
        "assertiveness": float(data.get("assertiveness", 0.5)),
        "openness": float(data.get("openness", 0.5)),
        "agreeableness": float(data.get("agreeableness", 0.5)),
        "conscientiousness": float(data.get("conscientiousness", 0.5)),
        "political_savvy": float(data.get("political_savvy", 0.5)),
    })

    stk = Stakeholder(
        id=sid,
        name=name,
        role=role,
        organization=org,
        tier=tier,
        personality=personality,
        goals=data.get("goals", []),
        vulnerabilities=data.get("vulnerabilities", []),
        allies=data.get("allies", []),
        rivals=data.get("rivals", []),
    )
    STATE.add_stakeholder(stk)
    save_state_to_file(STATE, DATA_FILE)
    return jsonify({"success": True, "stakeholder": stk.to_dict()}), 201


@app.route("/api/interaction", methods=["POST"])
def api_create_interaction():
    """Record a new interaction and incrementally update trust and entropy."""
    data = request.get_json() or {}
    src = data.get("source_id")
    tgt = data.get("target_id")
    
    if not src or not tgt or src not in STATE.stakeholders or tgt not in STATE.stakeholders:
        return jsonify({"error": "Valid source_id and target_id are required"}), 400

    type_str = data.get("type", "meeting").strip().lower()
    try:
        itype = InteractionType(type_str)
    except ValueError:
        itype = InteractionType.MEETING

    try:
        sent = Sentiment(int(data.get("sentiment", 0)))
    except (ValueError, TypeError):
        sent = Sentiment.NEUTRAL

    inter = Interaction(
        id=uuid.uuid4().hex[:8],
        timestamp=data.get("timestamp") or datetime.now().isoformat()[:10],
        type=itype,
        participants=[src, tgt],
        initiator=data.get("initiator", src),
        sentiment=sent,
        trust_delta=float(data.get("trust_delta", 0.0)),
        summary=data.get("summary", ""),
        context=data.get("context", ""),
        commitments_made=data.get("commitments_made", []),
        commitments_kept=data.get("commitments_kept"),
        power_move=bool(data.get("power_move", False)),
        concession_made=bool(data.get("concession_made", False)),
    )
    STATE.add_interaction(inter)

    # Update both directions of the relationship
    stk_src = STATE.stakeholders[src]
    stk_tgt = STATE.stakeholders[tgt]
    
    rel_forward = STATE.get_or_create_relationship(src, tgt)
    apply_interaction(rel_forward, inter, stk_src, stk_tgt)

    rel_backward = STATE.get_or_create_relationship(tgt, src)
    apply_interaction(rel_backward, inter, stk_tgt, stk_src)

    save_state_to_file(STATE, DATA_FILE)
    return jsonify({
        "success": True,
        "interaction": inter.to_dict(),
        "relationship_forward": rel_forward.to_dict(),
        "relationship_backward": rel_backward.to_dict(),
    }), 201


@app.route("/api/reset", methods=["POST"])
def api_reset_dataset():
    """Reset dataset to fresh baseline scenario."""
    global STATE
    STATE = generate_dataset(n_interactions=80, seed=42)
    save_state_to_file(STATE, DATA_FILE)
    return jsonify({"success": True, "message": "Dataset reset to default baseline"})


# --- AI Strategic Advisor ------------------------------------------------

def generate_builtin_briefing(stakeholder: Stakeholder, profile: Any, risk: Any, rels: list[dict], context: str) -> str:
    """Generates rule-based tactical briefing when no external LLM is configured."""
    dom_style = profile.dominant_style if profile else "collaborative"
    rel_score = profile.reliability_score if profile else 0.8
    risk_score = risk.risk_score if risk else 0.3
    factors = risk.factors if risk else []

    top_rels = sorted(rels, key=lambda x: x.get("trust", 0), reverse=True)[:3]
    allies_text = ", ".join([f"{r['other_name']} (Trust: {r['trust']})" for r in top_rels]) or "None established"

    return f"""# 🎯 Executive Strategic Briefing: {stakeholder.name}
**Role:** {stakeholder.role} — {stakeholder.organization} ({stakeholder.tier.value.upper()})
**Meeting Objective:** {context or 'General Strategic Alignment & Stakeholder Engagement'}

---

### 1. 🧠 Psychological Profile & Negotiation Stance
* **Dominant Negotiation Style:** `{dom_style.upper()}` (Reliability: {rel_score*100:.0f}%)
* **Behavioral Tendencies:**
  * Assertiveness: {stakeholder.personality.get('assertiveness', 0.5)*100:.0f}%
  * Political Savvy: {stakeholder.personality.get('political_savvy', 0.5)*100:.0f}%
  * Conscientiousness: {stakeholder.personality.get('conscientiousness', 0.5)*100:.0f}%
* **Strongest Ties:** {allies_text}

---

### 2. ⚠️ Risk Assessment & Vulnerabilities
* **Composite Relationship Risk:** `{risk_score:.2f}` ({'High Risk' if risk_score > 0.5 else 'Moderate' if risk_score > 0.3 else 'Healthy'})
* **Identified Vulnerabilities & Flags:**
  * Goals: {', '.join(stakeholder.goals) if stakeholder.goals else 'Maintaining divisional autonomy and standing.'}
  * Vulnerabilities: {', '.join(stakeholder.vulnerabilities) if stakeholder.vulnerabilities else 'Sensitive to authority challenges.'}
  * Risk Factors: {', '.join(factors) if factors else 'None detected.'}

---

### 3. 🛡️ Tactical Playbook & Negotiation Strategy
* **Opening Strategy:** Frame discussion around mutual organizational wins. Acknowledge their institutional standing early.
* **Leverage Points:** Align your proposal directly with their core goal: *"{stakeholder.goals[0] if stakeholder.goals else stakeholder.role}"*.
* **Concession Architecture:** Never concede without extracting a concrete reciprocal commitment.
* **Red Lines & Pitfalls to Avoid:** Avoid ambiguous timeline promises or dismissive responses to their status concerns.
"""


@app.route("/api/advisor/briefing", methods=["POST"])
def api_advisor_briefing():
    """Generates an actionable tactical briefing for a stakeholder using Builtin, Gemini, OpenAI, or Claude."""
    data = request.get_json() or {}
    sid = data.get("stakeholder_id")
    context = data.get("context", "").strip()
    provider = data.get("provider", "builtin").strip().lower()
    api_key = data.get("apiKey", "").strip()
    model = data.get("model", "").strip()

    s = STATE.stakeholders.get(sid)
    if not s:
        return jsonify({"error": "Stakeholder not found"}), 404

    profiles = build_all_profiles(STATE)
    profile = profiles.get(sid)
    risk = full_risk_report(STATE).get(sid)

    rels = []
    for r in STATE.get_stakeholder_relationships(sid):
        if r.interaction_count > 0:
            other_id = r.target_id if r.source_id == sid else r.source_id
            other = STATE.stakeholders.get(other_id)
            if other:
                rels.append({"other_name": other.name, "trust": round(r.trust_score, 2)})

    if provider == "builtin" or not api_key:
        briefing = generate_builtin_briefing(s, profile, risk, rels, context)
        return jsonify({"output": briefing, "provider": "builtin"})

    # Prepare structured prompt for live LLM
    prompt_payload = f"""You are a master corporate intelligence strategist and negotiation psychologist.
Provide a high-stakes, concise tactical negotiation briefing for an upcoming engagement with:

Stakeholder Name: {s.name}
Role & Title: {s.role} at {s.organization} (Tier: {s.tier.value})
Goals: {', '.join(s.goals)}
Vulnerabilities: {', '.join(s.vulnerabilities)}
Personality Scores: {json.dumps(s.personality)}
Dominant Negotiation Style: {profile.dominant_style if profile else 'collaborative'} (Reliability: {profile.reliability_score if profile else 0.8})
Risk Factors: {json.dumps(risk.factors if risk else [])}
Top Network Ties: {json.dumps(rels[:4])}
Specific Engagement Context: {context or 'Upcoming strategic negotiation'}

Generate a structured markdown executive briefing with:
1. Stakeholder Diagnosis (Mindset, Drivers, Hidden Agendas)
2. Strategic Leverage & Vulnerability Exploits
3. Tactical Playbook (Opening, Trade-offs, Closing)
4. Golden Rules & Pitfalls to Avoid
Be tactical, direct, analytical, and actionable. No fluff."""

    try:
        if provider == "gemini":
            target_model = model or "gemini-2.0-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
            req_body = json.dumps({
                "contents": [{"parts": [{"text": prompt_payload}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1500}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=req_body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                output = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"output": output, "provider": "gemini", "model": target_model})

        elif provider == "openai":
            target_model = model or "gpt-4o-mini"
            url = "https://api.openai.com/v1/chat/completions"
            req_body = json.dumps({
                "model": target_model,
                "messages": [
                    {"role": "system", "content": "You are a master corporate intelligence strategist."},
                    {"role": "user", "content": prompt_payload}
                ],
                "temperature": 0.3
            }).encode("utf-8")
            req = urllib.request.Request(url, data=req_body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                output = res_data["choices"][0]["message"]["content"]
                return jsonify({"output": output, "provider": "openai", "model": target_model})

        elif provider == "anthropic":
            target_model = model or "claude-3-5-sonnet-20241022"
            url = "https://api.anthropic.com/v1/messages"
            req_body = json.dumps({
                "model": target_model,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt_payload}]
            }).encode("utf-8")
            req = urllib.request.Request(url, data=req_body, headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                output = res_data["content"][0]["text"]
                return jsonify({"output": output, "provider": "anthropic", "model": target_model})

        else:
            briefing = generate_builtin_briefing(s, profile, risk, rels, context)
            return jsonify({"output": briefing, "provider": "builtin"})

    except Exception as e:
        return jsonify({"error": f"LLM API Error: {str(e)}"}), 500


# --- Server Runner -------------------------------------------------------

def run_app(port: int = 5088):
    """Starts the Flask server with automatic port conflict handling."""
    target_port = find_free_port(port)
    if target_port != port:
        print(f"\n⚠️  [INFO] Port {port} was busy. Automatically switched to port {target_port}.")

    print("\n  =======================================================")
    print("  🚀 Strategic Memory CRM — Behavioral Intelligence Engine")
    print(f"  📡 Web Dashboard : http://localhost:{target_port}")
    print(f"  🕸️ Graph View    : http://localhost:{target_port}/graph")
    print(f"  💾 Data Storage  : {DATA_FILE}")
    print("  =======================================================\n")
    app.run(debug=False, host="0.0.0.0", port=target_port)


if __name__ == "__main__":
    run_app()
