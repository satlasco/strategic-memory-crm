"""Automated unit tests for Strategic Memory CRM MCP tools and server."""

import json
import unittest

from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm import mcp_tools


class TestMCPTools(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=40, seed=42)

    def test_list_stakeholders(self):
        res = mcp_tools.list_stakeholders(self.state)
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        first = res[0]
        self.assertIn("id", first)
        self.assertIn("name", first)
        self.assertIn("role", first)
        self.assertIn("dominant_style", first)
        self.assertIn("risk_score", first)

    def test_get_stakeholder_intel(self):
        # By ID
        first_id = list(self.state.stakeholders.keys())[0]
        intel = mcp_tools.get_stakeholder_intel(self.state, first_id)
        self.assertNotIn("error", intel)
        self.assertIn("stakeholder", intel)
        self.assertIn("negotiation_profile", intel)
        self.assertIn("risk_assessment", intel)
        self.assertIn("key_relationships", intel)

        # By Name (case-insensitive)
        first_name = self.state.stakeholders[first_id].name
        intel_name = mcp_tools.get_stakeholder_intel(self.state, first_name.upper())
        self.assertNotIn("error", intel_name)
        self.assertEqual(intel_name["stakeholder"]["id"], first_id)

    def test_get_organization_politics(self):
        pol = mcp_tools.get_organization_politics(self.state)
        self.assertIn("network_overview", pol)
        self.assertIn("informal_influencers_pagerank", pol)
        self.assertIn("information_bridges_betweenness", pol)
        self.assertIn("gatekeepers", pol)
        self.assertIn("brokers_articulation_points", pol)
        self.assertIn("detected_coalitions", pol)

    def test_analyze_relationship(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        rel_info = mcp_tools.analyze_relationship(self.state, s1, s2)
        self.assertNotIn("error", rel_info)
        self.assertIn("trust_score", rel_info)
        self.assertIn("trust_trajectory", rel_info)
        self.assertIn("relationship_entropy", rel_info)
        self.assertIn("relationship_risk", rel_info)

    def test_log_interaction(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        res = mcp_tools.log_interaction(
            state=self.state,
            source_id=s1,
            target_id=s2,
            interaction_type="meeting",
            summary="Discussed strategic integration roadmap.",
            sentiment="positive",
            commitments_made=["Deliver Q3 milestone"],
            commitments_kept=True,
            concession_made=False
        )
        self.assertEqual(res.get("status"), "success")
        self.assertIn("updated_trust_score", res)

    def test_add_stakeholder(self):
        res = mcp_tools.add_stakeholder(
            state=self.state,
            name="Elena Rostova",
            role="Chief Strategy Officer",
            organization="Apex Dynamics",
            org_tier="c_suite",
            personality={"assertiveness": 0.8, "political_savvy": 0.9},
            goals=["Lead market consolidation"],
            vulnerabilities=["Reputational risk"]
        )
        self.assertEqual(res.get("status"), "success")
        sid = res.get("stakeholder_id")
        self.assertIn(sid, self.state.stakeholders)
        self.assertEqual(self.state.stakeholders[sid].name, "Elena Rostova")

    def test_generate_tactical_briefing(self):
        first_id = list(self.state.stakeholders.keys())[0]
        briefing_res = mcp_tools.generate_tactical_briefing(
            self.state,
            first_id,
            meeting_objective="Negotiate commercial terms"
        )
        self.assertNotIn("error", briefing_res)
        self.assertIn("briefing", briefing_res)
        self.assertIn("key_metrics", briefing_res)
        self.assertIn("Executive Strategic Briefing", briefing_res["briefing"])



    def test_mcp_simulate_scenario(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        res = mcp_tools.simulate_scenario(self.state, "broken_commitment", s1, s2)
        self.assertEqual(res.get("status"), "success")
        self.assertIn("impact_summary", res)

    def test_mcp_get_coalition_radar(self):
        res = mcp_tools.get_coalition_radar(self.state)
        self.assertIn("balance_of_power", res)

    def test_mcp_compare_stakeholders(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        res = mcp_tools.compare_stakeholders(self.state, s1, s2)
        self.assertNotIn("error", res)
        self.assertIn("stakeholder_1", res)
        self.assertIn("stakeholder_2", res)
        self.assertIn("dyadic_dynamics", res)


if __name__ == "__main__":
    unittest.main()
