"""Comprehensive unit and integration test suite for Strategic Memory CRM."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from strategic_memory_crm.coalitions import analyze_coalitions_and_power
from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm.entropy import compute_entropy, network_entropy
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    OrgTier,
    Relationship,
    Sentiment,
    Stakeholder,
)
from strategic_memory_crm.negotiation import (
    build_all_profiles,
    build_negotiation_profile,
    detect_reciprocal_pairs,
)
from strategic_memory_crm.risk import assess_relationship_risk, full_risk_report
from strategic_memory_crm.scenario_simulator import simulate_what_if
from strategic_memory_crm.storage import load_state_from_file, save_state_to_file
from strategic_memory_crm.trust import (
    apply_interaction,
    compute_trust_trajectory,
    passive_decay,
    personality_compatibility,
)


class TestTrustDynamics(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=30, seed=42)

    def test_personality_compatibility(self):
        s1 = self.state.stakeholders[list(self.state.stakeholders.keys())[0]]
        s2 = self.state.stakeholders[list(self.state.stakeholders.keys())[1]]
        compat = personality_compatibility(s1, s2)
        self.assertIsInstance(compat, float)
        self.assertGreaterEqual(compat, -1.0)
        self.assertLessEqual(compat, 1.0)

    def test_apply_interaction_positive_boosts_trust(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = self.state.stakeholders[sids[0]], self.state.stakeholders[sids[1]]
        rel = Relationship(source_id=s1.id, target_id=s2.id, trust_score=0.5)

        inter = Interaction(
            id="test1",
            type=InteractionType.MEETING,
            participants=[s1.id, s2.id],
            initiator=s1.id,
            sentiment=Sentiment.VERY_POSITIVE,
            commitments_kept=True
        )
        delta = apply_interaction(rel, inter, s1, s2)
        self.assertGreater(delta, 0.0)
        self.assertGreater(rel.trust_score, 0.5)

    def test_apply_interaction_betrayal_severely_penalizes_trust(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = self.state.stakeholders[sids[0]], self.state.stakeholders[sids[1]]
        rel = Relationship(source_id=s1.id, target_id=s2.id, trust_score=0.8)

        inter = Interaction(
            id="test2",
            type=InteractionType.BETRAYAL,
            participants=[s1.id, s2.id],
            initiator=s1.id,
            sentiment=Sentiment.VERY_NEGATIVE,
            commitments_kept=False
        )
        delta = apply_interaction(rel, inter, s1, s2)
        self.assertLess(delta, 0.0)
        self.assertLess(rel.trust_score, 0.6)

    def test_passive_decay(self):
        sids = list(self.state.stakeholders.keys())
        rel = self.state.get_or_create_relationship(sids[0], sids[1])
        rel.trust_score = 0.9
        passive_decay(rel, days_elapsed=30)
        self.assertLess(rel.trust_score, 0.9)


class TestNegotiationAndInfluence(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=50, seed=42)

    def test_negotiation_profile_generation(self):
        sid = list(self.state.stakeholders.keys())[0]
        prof = build_negotiation_profile(self.state, sid)
        self.assertEqual(prof.stakeholder_id, sid)
        self.assertIn(prof.dominant_style, ["dominator", "accommodator", "collaborator", "competitor", "unknown"])

    def test_influence_pagerank_and_betweenness(self):
        inf = analyze_influence(self.state)
        self.assertGreater(len(inf.pagerank), 0)
        self.assertGreater(len(inf.betweenness), 0)
        self.assertIsInstance(inf.coalitions, list)


class TestEntropyAndRisk(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=40, seed=42)

    def test_relationship_entropy(self):
        sids = list(self.state.stakeholders.keys())
        rel = self.state.get_or_create_relationship(sids[0], sids[1])
        breakdown = compute_entropy(rel, self.state)
        self.assertGreaterEqual(breakdown.composite_entropy, 0.0)

    def test_network_entropy(self):
        net_ent = network_entropy(self.state)
        self.assertGreaterEqual(net_ent, 0.0)

    def test_full_risk_report(self):
        report = full_risk_report(self.state)
        self.assertEqual(len(report), len(self.state.stakeholders))
        first_r = list(report.values())[0]
        self.assertGreaterEqual(first_r.risk_score, 0.0)
        self.assertLessEqual(first_r.risk_score, 1.0)


class TestScenarioAndCoalitions(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=40, seed=42)

    def test_scenario_simulator(self):
        sids = list(self.state.stakeholders.keys())
        s1, s2 = sids[0], sids[1]

        # Conflict simulation
        res = simulate_what_if(self.state, "conflict", s1, s2, severity=1.5)
        self.assertEqual(res["status"], "success")
        self.assertIn("impact_summary", res)
        self.assertIn("risk_shifts", res)
        self.assertIn("trust_shifts", res)
        self.assertIn("strategic_mitigations", res)

        # Passive decay simulation
        res_decay = simulate_what_if(self.state, "passive_decay", s1, time_lapse_days=60)
        self.assertEqual(res_decay["status"], "success")
        self.assertIn("simulated_entropy", res_decay["impact_summary"])

    def test_coalition_radar(self):
        res = analyze_coalitions_and_power(self.state)
        self.assertIn("total_factions", res)
        self.assertIn("balance_of_power", res)
        self.assertGreater(len(res["balance_of_power"]), 0)
        first_faction = res["balance_of_power"][0]
        self.assertIn("name", first_faction)
        self.assertIn("power_share_percentage", first_faction)
        self.assertIn("members", first_faction)


class TestStorageAndPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = Path(self.temp_dir) / "test_state.json"
        self.state = generate_dataset(n_interactions=20, seed=42)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        save_state_to_file(self.state, self.file_path)
        self.assertTrue(self.file_path.exists())

        loaded = load_state_from_file(self.file_path)
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded.stakeholders), len(self.state.stakeholders))
        self.assertEqual(len(loaded.interactions), len(self.state.interactions))


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        from app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_dashboard_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Relationship Intelligence", res.data)

    def test_graph_route(self):
        res = self.client.get("/graph")
        self.assertEqual(res.status_code, 200)

    def test_simulator_route(self):
        res = self.client.get("/simulator")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Scenario Simulator", res.data)

    def test_coalitions_route(self):
        res = self.client.get("/coalitions")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Coalition Radar", res.data)

    def test_dyad_route(self):
        res = self.client.get("/dyad")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Dyadic Comparison", res.data)

    def test_api_state(self):
        res = self.client.get("/api/state")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("stakeholders", data)

    def test_api_simulator_run(self):
        from app import STATE
        sids = list(STATE.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        res = self.client.post("/api/simulator/run", json={
            "scenario_type": "conflict",
            "source_id": s1,
            "target_id": s2,
            "severity": 1.2
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get("status"), "success")

    def test_api_coalitions(self):
        res = self.client.get("/api/coalitions")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("balance_of_power", data)

    def test_api_dyad(self):
        from app import STATE
        sids = list(STATE.stakeholders.keys())
        s1, s2 = sids[0], sids[1]
        res = self.client.get(f"/api/dyad?src={s1}&tgt={s2}")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("stakeholder_1", data)


if __name__ == "__main__":
    unittest.main()
