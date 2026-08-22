"""Strategic Memory CRM — Unified MCP Server & Web CLI Entry Point.

Run directly for MCP stdio mode (Claude Desktop, Cursor, Antigravity):
    python mcp_server.py
    uvx strategic-memory-crm

Run with --web to launch the Flask Web Dashboard:
    python mcp_server.py --web
    strategic-memory-crm --web
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from mcp.server.fastmcp import FastMCP

from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm.models import CRMState
from strategic_memory_crm.storage import load_state_from_file, save_state_to_file
from strategic_memory_crm import mcp_tools

# Data storage path (resolves locally or relative to package)
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "crm_state.json"


def get_state() -> CRMState:
    """Loads current CRMState from disk or generates default baseline."""
    state = load_state_from_file(DATA_FILE)
    if state is None or len(state.stakeholders) == 0:
        state = generate_dataset(n_interactions=80, seed=42)
        save_state_to_file(state, DATA_FILE)
    return state


def persist_state(state: CRMState) -> None:
    """Saves updated CRMState to disk."""
    save_state_to_file(state, DATA_FILE)


# Initialize FastMCP Server
mcp = FastMCP(
    "strategic-memory-crm",
    instructions="Strategic Relationship Intelligence CRM for modeling trust dynamics, negotiation patterns, informal organizational politics, and tactical pre-meeting battleplans."
)


@mcp.tool()
def list_stakeholders() -> str:
    """List all stakeholders with their role, organization, tier, personality traits, dominant negotiation style, and risk level."""
    state = get_state()
    res = mcp_tools.list_stakeholders(state)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def get_stakeholder_intel(stakeholder_id: str) -> str:
    """Get deep behavioral intelligence for a stakeholder: trust ties with peers, negotiation style, commitment reliability, risk drivers, allies/rivals, and recent interactions. Can provide either stakeholder ID (e.g. 'marcus_vance') or full name (e.g. 'Marcus Vance')."""
    state = get_state()
    res = mcp_tools.get_stakeholder_intel(state, stakeholder_id)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def get_organization_politics() -> str:
    """Analyze the informal power structure, key influencers (PageRank), information bridges & gatekeepers (betweenness), detected hidden coalitions, and overall relationship network entropy."""
    state = get_state()
    res = mcp_tools.get_organization_politics(state)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def analyze_relationship(source_id: str, target_id: str) -> str:
    """Analyze the dyadic relationship between two stakeholders: asymmetric trust, reciprocity balance, entropy (volatility), risk rating, and shared interaction history. Can provide IDs or names."""
    state = get_state()
    res = mcp_tools.analyze_relationship(state, source_id, target_id)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def log_interaction(
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
) -> str:
    """Log a new interaction (meeting, email, phone_call, negotiation, favor, conflict, betrayal) between two stakeholders. Automatically calculates dynamic trust decay/growth, updates reciprocity balance, and saves state to database."""
    state = get_state()
    res = mcp_tools.log_interaction(
        state=state,
        source_id=source_id,
        target_id=target_id,
        interaction_type=interaction_type,
        summary=summary,
        context=context,
        sentiment=sentiment,
        commitments_made=commitments_made,
        commitments_kept=commitments_kept,
        concession_made=concession_made,
        power_move=power_move,
    )
    if res.get("status") == "success":
        persist_state(state)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def add_stakeholder(
    name: str,
    role: str,
    organization: str,
    org_tier: str = "individual",
    personality: Optional[dict[str, float]] = None,
    goals: Optional[list[str]] = None,
    vulnerabilities: Optional[list[str]] = None,
    allies: Optional[list[str]] = None,
    rivals: Optional[list[str]] = None
) -> str:
    """Add a new stakeholder to the Strategic Memory CRM database with optional personality traits (assertiveness, openness, agreeableness, conscientiousness, political_savvy), goals, vulnerabilities, allies, and rivals. Tiers: 'c_suite', 'vp', 'director', 'manager', 'individual', 'external'."""
    state = get_state()
    res = mcp_tools.add_stakeholder(
        state=state,
        name=name,
        role=role,
        organization=organization,
        org_tier=org_tier,
        personality=personality,
        goals=goals,
        vulnerabilities=vulnerabilities,
        allies=allies,
        rivals=rivals,
    )
    if res.get("status") == "success":
        persist_state(state)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def generate_tactical_briefing(stakeholder_id: str, meeting_objective: str = "") -> str:
    """Generate an executive-level pre-meeting tactical battleplan, psychological leverage analysis, negotiation moves, and critical pitfalls for an upcoming interaction with a stakeholder."""
    state = get_state()
    res = mcp_tools.generate_tactical_briefing(state, stakeholder_id, meeting_objective)
    return json.dumps(res, indent=2, ensure_ascii=False)




@mcp.tool()
def simulate_scenario(
    scenario_type: str,
    source_id: str,
    target_id: Optional[str] = None,
    severity: float = 1.0,
    time_lapse_days: int = 0,
    description: str = ""
) -> str:
    """Run a predictive what-if simulation (scenario_type: 'conflict', 'broken_commitment', 'kept_commitment', 'strategic_favor', 'betrayal', 'passive_decay') to project network entropy shifts, trust ripples, contagion nodes, and tactical containment advice."""
    state = get_state()
    res = mcp_tools.simulate_scenario(
        state=state,
        scenario_type=scenario_type,
        source_id=source_id,
        target_id=target_id,
        severity=severity,
        time_lapse_days=time_lapse_days,
        description=description
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def get_coalition_radar() -> str:
    """Analyze corporate factions, informal voting blocs, collective decision power share (%), faction leaders, and weakest links in the network."""
    state = get_state()
    res = mcp_tools.get_coalition_radar(state)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def compare_stakeholders(source_id: str, target_id: str) -> str:
    """Compare two stakeholders side-by-side: Big-Five psychometrics, negotiation typologies, bidirectional trust scores, reciprocity balance, and shared allies/rivals."""
    state = get_state()
    res = mcp_tools.compare_stakeholders(state, source_id, target_id)
    return json.dumps(res, indent=2, ensure_ascii=False)


def main() -> None:
    """CLI Entry Point: default is MCP stdio server; if --web passed, launches Flask dashboard."""
    parser = argparse.ArgumentParser(description="Strategic Memory CRM — Behavioral Intelligence & MCP Server")
    parser.add_argument("--web", action="store_true", help="Launch the Flask web dashboard instead of MCP stdio server")
    parser.add_argument("--port", type=int, default=5088, help="Port for the web dashboard (default: 5088)")
    args, unknown = parser.parse_known_args()

    if args.web:
        from app import app
        print(f"🚀 Starting Strategic Memory CRM Web Dashboard on http://localhost:{args.port}")
        app.run(host="0.0.0.0", port=args.port, debug=False)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
