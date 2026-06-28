"""Realistic fictional dataset generator.

Creates a plausible scenario of two merging tech companies
(Meridian Systems and Vantage Analytics) with stakeholders
across leadership, engineering, product, and external advisory roles.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import CRMState, OrgTier, Stakeholder
from .simulation import simulate_interactions
from .trust import rebuild_trust_scores
from .entropy import compute_all_entropy
from .risk import full_risk_report
from .negotiation import build_all_profiles
from .influence import analyze_influence


def create_stakeholders() -> list[Stakeholder]:
    """Define a realistic cast of stakeholders for the merger scenario."""
    return [
        # --- Meridian Systems (acquiring company) ---
        Stakeholder(
            id="ms_ceo",
            name="Diana Kessler",
            role="CEO",
            organization="Meridian Systems",
            tier=OrgTier.C_SUITE,
            personality={
                "assertiveness": 0.85, "openness": 0.6,
                "agreeableness": 0.4, "conscientiousness": 0.8,
                "political_savvy": 0.9,
            },
            goals=["Complete acquisition smoothly", "Retain key Vantage talent",
                   "Achieve 30% cost synergy within 18 months"],
            vulnerabilities=["Board pressure on deal ROI", "Talent flight risk"],
            allies=["ms_cfo", "ms_vpe"],
            rivals=["va_ceo"],
        ),
        Stakeholder(
            id="ms_cfo",
            name="Robert Tanaka",
            role="CFO",
            organization="Meridian Systems",
            tier=OrgTier.C_SUITE,
            personality={
                "assertiveness": 0.7, "openness": 0.3,
                "agreeableness": 0.5, "conscientiousness": 0.9,
                "political_savvy": 0.7,
            },
            goals=["Control integration costs", "Validate financial projections"],
            vulnerabilities=["Risk-averse reputation", "Limited tech understanding"],
            allies=["ms_ceo", "ms_dir_ops"],
            rivals=["va_cfo"],
        ),
        Stakeholder(
            id="ms_vpe",
            name="Samira Okafor",
            role="VP of Engineering",
            organization="Meridian Systems",
            tier=OrgTier.VP,
            personality={
                "assertiveness": 0.6, "openness": 0.8,
                "agreeableness": 0.7, "conscientiousness": 0.75,
                "political_savvy": 0.5,
            },
            goals=["Integrate tech stacks", "Build unified engineering culture"],
            vulnerabilities=["Stretched across too many initiatives"],
            allies=["ms_ceo", "va_eng_lead"],
            rivals=["ms_dir_product"],
        ),
        Stakeholder(
            id="ms_dir_product",
            name="Marcus Webb",
            role="Director of Product",
            organization="Meridian Systems",
            tier=OrgTier.DIRECTOR,
            personality={
                "assertiveness": 0.75, "openness": 0.5,
                "agreeableness": 0.35, "conscientiousness": 0.6,
                "political_savvy": 0.8,
            },
            goals=["Own combined product roadmap", "Eliminate redundant product lines"],
            vulnerabilities=["Territorial about product decisions", "Weak engineering rapport"],
            allies=["ms_dir_ops"],
            rivals=["ms_vpe", "va_vp_product"],
        ),
        Stakeholder(
            id="ms_dir_ops",
            name="Linda Chen",
            role="Director of Operations",
            organization="Meridian Systems",
            tier=OrgTier.DIRECTOR,
            personality={
                "assertiveness": 0.5, "openness": 0.4,
                "agreeableness": 0.65, "conscientiousness": 0.85,
                "political_savvy": 0.6,
            },
            goals=["Streamline merged operations", "Reduce headcount overlap"],
            vulnerabilities=["Seen as cost-cutter, not innovator"],
            allies=["ms_cfo", "ms_dir_product"],
            rivals=[],
        ),

        # --- Vantage Analytics (acquired company) ---
        Stakeholder(
            id="va_ceo",
            name="James Holloway",
            role="CEO (outgoing)",
            organization="Vantage Analytics",
            tier=OrgTier.C_SUITE,
            personality={
                "assertiveness": 0.8, "openness": 0.7,
                "agreeableness": 0.45, "conscientiousness": 0.65,
                "political_savvy": 0.85,
            },
            goals=["Secure favorable exit terms", "Protect Vantage team members",
                   "Maintain legacy and reputation"],
            vulnerabilities=["Lame-duck authority", "Emotional attachment to company"],
            allies=["va_cfo", "va_vp_product", "ext_advisor"],
            rivals=["ms_ceo"],
        ),
        Stakeholder(
            id="va_cfo",
            name="Priya Sharma",
            role="CFO",
            organization="Vantage Analytics",
            tier=OrgTier.C_SUITE,
            personality={
                "assertiveness": 0.55, "openness": 0.5,
                "agreeableness": 0.6, "conscientiousness": 0.85,
                "political_savvy": 0.65,
            },
            goals=["Negotiate retention packages", "Ensure accurate asset valuation"],
            vulnerabilities=["Uncertain about own role post-merger"],
            allies=["va_ceo", "ms_cfo"],
            rivals=[],
        ),
        Stakeholder(
            id="va_vp_product",
            name="Elena Vasquez",
            role="VP of Product",
            organization="Vantage Analytics",
            tier=OrgTier.VP,
            personality={
                "assertiveness": 0.7, "openness": 0.85,
                "agreeableness": 0.5, "conscientiousness": 0.7,
                "political_savvy": 0.7,
            },
            goals=["Preserve Vantage's product vision", "Secure leadership role in merged entity"],
            vulnerabilities=["Direct competition with Marcus Webb for product leadership"],
            allies=["va_ceo", "va_eng_lead"],
            rivals=["ms_dir_product"],
        ),
        Stakeholder(
            id="va_eng_lead",
            name="Tomás Rivera",
            role="Engineering Lead",
            organization="Vantage Analytics",
            tier=OrgTier.MANAGER,
            personality={
                "assertiveness": 0.45, "openness": 0.9,
                "agreeableness": 0.8, "conscientiousness": 0.8,
                "political_savvy": 0.3,
            },
            goals=["Protect team from layoffs", "Advocate for Vantage's tech architecture"],
            vulnerabilities=["Politically naive", "Over-reliant on technical merit"],
            allies=["ms_vpe", "va_vp_product"],
            rivals=[],
        ),
        Stakeholder(
            id="va_mgr_data",
            name="Aisha Mbeki",
            role="Data Science Manager",
            organization="Vantage Analytics",
            tier=OrgTier.MANAGER,
            personality={
                "assertiveness": 0.6, "openness": 0.75,
                "agreeableness": 0.55, "conscientiousness": 0.7,
                "political_savvy": 0.4,
            },
            goals=["Retain data science team", "Secure budget for ML initiatives"],
            vulnerabilities=["Team seen as cost center by Meridian finance"],
            allies=["va_eng_lead"],
            rivals=["ms_dir_ops"],
        ),

        # --- External ---
        Stakeholder(
            id="ext_advisor",
            name="Catherine Blackwood",
            role="M&A Advisor",
            organization="Blackwood & Associates",
            tier=OrgTier.EXTERNAL,
            personality={
                "assertiveness": 0.75, "openness": 0.6,
                "agreeableness": 0.4, "conscientiousness": 0.8,
                "political_savvy": 0.95,
            },
            goals=["Maximize deal value", "Maintain long-term client relationships"],
            vulnerabilities=["Conflicts of interest across clients"],
            allies=["va_ceo", "ms_ceo"],
            rivals=[],
        ),
        Stakeholder(
            id="ext_board",
            name="Philip Raines",
            role="Board Member (Meridian)",
            organization="Meridian Board",
            tier=OrgTier.C_SUITE,
            personality={
                "assertiveness": 0.65, "openness": 0.35,
                "agreeableness": 0.3, "conscientiousness": 0.7,
                "political_savvy": 0.8,
            },
            goals=["Ensure shareholder value", "Oversight of integration risk"],
            vulnerabilities=["Limited operational visibility"],
            allies=["ms_ceo"],
            rivals=[],
        ),
    ]


def generate_dataset(
    n_interactions: int = 80,
    seed: int = 42,
    output_dir: str | None = None,
) -> CRMState:
    """Build the full dataset: stakeholders, simulated interactions, computed scores."""
    state = CRMState()

    for s in create_stakeholders():
        state.add_stakeholder(s)

    simulate_interactions(state, n_interactions=n_interactions, seed=seed)
    rebuild_trust_scores(state)
    compute_all_entropy(state)
    full_risk_report(state)

    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "crm_state.json", "w") as f:
            json.dump(state.to_dict(), f, indent=2)

        profiles = build_all_profiles(state)
        with open(out / "negotiation_profiles.json", "w") as f:
            json.dump({k: v.to_dict() for k, v in profiles.items()}, f, indent=2)

        influence = analyze_influence(state)
        with open(out / "influence_report.json", "w") as f:
            json.dump(influence.to_dict(), f, indent=2)

    return state


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "generated")
    state = generate_dataset(output_dir=data_dir)
    print(f"Generated {len(state.stakeholders)} stakeholders, "
          f"{len(state.interactions)} interactions, "
          f"{len(state.relationships)} relationships")
