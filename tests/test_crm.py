"""Comprehensive Unit Test Suite for Strategic Memory CRM."""

import json
import tempfile
import unittest
from pathlib import Path
import sys

# Ensure strategic_memory_crm is importable
CRM_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(CRM_ROOT))

from app import app, generate_builtin_briefing
from strategic_memory_crm.dataset import generate_dataset
from strategic_memory_crm.entropy import (
    _interaction_regularity,
    _shannon_entropy,
    _trust_volatility,
    compute_all_entropy,
    compute_entropy,
    network_entropy,
)
from strategic_memory_crm.influence import analyze_influence
from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    OrgTier,
    PersonalityAxis,
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
from strategic_memory_crm.storage import load_state_from_file, save_state_to_file
from strategic_memory_crm.trust import (
    apply_interaction,
    compute_trust_trajectory,
    passive_decay,
    personality_compatibility,
)


class TestTrustDynamics(unittest.TestCase):
    def setUp(self):
        self.alice = Stakeholder(id="alice", name="Alice", personality={"assertiveness": 0.8, "agreeableness": 0.3})
        self.bob = Stakeholder(id="bob", name="Bob", personality={"assertiveness": 0.7, "agreeableness": 0.4})
        self.rel = Relationship(source_id="alice", target_id="bob", trust_score=0.5)

    def test_personality_compatibility(self):
        compat = personality_compatibility(self.alice, self.bob)
        self.assertIsInstance(compat, float)
        self.assertGreater(compat, 0.0)

    def test_apply_interaction_positive(self):
        inter = Interaction(
            id="int1",
            type=InteractionType.MEETING,
            participants=["alice", "bob"],
            initiator="alice",
            sentiment=Sentiment.VERY_POSITIVE,
            commitments_kept=True,
        )
        delta = apply_interaction(self.rel, inter, self.alice, self.bob)
        self.assertGreater(delta, 0.0)
        self.assertGreater(self.rel.trust_score, 0.5)
        self.assertEqual(self.rel.interaction_count, 1)

    def test_apply_interaction_betrayal(self):
        inter = Interaction(
            id="int2",
            type=InteractionType.BETRAYAL,
            participants=["alice", "bob"],
            initiator="bob",
            sentiment=Sentiment.VERY_NEGATIVE,
            commitments_kept=False,
        )
        delta = apply_interaction(self.rel, inter, self.alice, self.bob)
        self.assertLess(delta, 0.0)
        self.assertLess(self.rel.trust_score, 0.5)

    def test_passive_decay(self):
        # Trust above 0.5 decays down toward 0.5
        self.rel.trust_score = 0.9
        delta = passive_decay(self.rel, days_elapsed=20)
        self.assertLess(delta, 0.0)
        self.assertLess(self.rel.trust_score, 0.9)
        self.assertGreaterEqual(self.rel.trust_score, 0.5)

    def test_trust_trajectory(self):
        self.rel.sentiment_history = [1, 2, 2, 2]
        traj = compute_trust_trajectory(self.rel)
        self.assertIn(traj, ["improving", "stable_high", "stable_neutral", "volatile", "deteriorating", "critical"])


class TestNegotiationAndInfluence(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=40, seed=42)

    def test_negotiation_profiles(self):
        profiles = build_all_profiles(self.state)
        self.assertGreater(len(profiles), 0)
        first_sid = list(profiles.keys())[0]
        p = profiles[first_sid]
        self.assertIn(p.dominant_style, ["dominator", "accommodator", "collaborator", "competitor", "avoider"])
        self.assertGreaterEqual(p.reliability_score, 0.0)
        self.assertLessEqual(p.reliability_score, 1.0)

    def test_detect_reciprocal_pairs(self):
        pairs = detect_reciprocal_pairs(self.state)
        self.assertIsInstance(pairs, list)

    def test_influence_analysis(self):
        inf = analyze_influence(self.state)
        self.assertGreater(len(inf.power_score), 0)
        self.assertGreater(len(inf.pagerank), 0)
        self.assertIsInstance(inf.gatekeepers, list)
        self.assertIsInstance(inf.brokers, list)
        self.assertIsInstance(inf.coalitions, list)


class TestEntropyAndRisk(unittest.TestCase):
    def setUp(self):
        self.state = generate_dataset(n_interactions=50, seed=42)

    def test_shannon_entropy(self):
        # Uniform distribution has high entropy
        values = [1, 2, 0, -1, -2]
        ent = _shannon_entropy(values)
        self.assertGreater(ent, 0.5)

        # Single value has 0 entropy
        self.assertEqual(_shannon_entropy([1, 1, 1, 1]), 0.0)

    def test_network_entropy(self):
        net_ent = network_entropy(self.state)
        self.assertGreaterEqual(net_ent, 0.0)
        self.assertLessEqual(net_ent, 1.0)

    def test_full_risk_report(self):
        report = full_risk_report(self.state)
        self.assertEqual(len(report), len(self.state.stakeholders))
        for sid, r in report.items():
            self.assertGreaterEqual(r.risk_score, 0.0)
            self.assertLessEqual(r.risk_score, 1.0)
            self.assertIsInstance(r.factors, list)


class TestStorageAndPersistence(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        state = generate_dataset(n_interactions=20, seed=42)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            saved = save_state_to_file(state, temp_path)
            self.assertTrue(saved)

            loaded_state = load_state_from_file(temp_path)
            self.assertIsNotNone(loaded_state)
            self.assertEqual(len(loaded_state.stakeholders), len(state.stakeholders))
            self.assertEqual(len(loaded_state.interactions), len(state.interactions))
            self.assertEqual(len(loaded_state.relationships), len(state.relationships))
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_dashboard_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Relationship Intelligence Dashboard", res.data)

    def test_graph_route(self):
        res = self.client.get("/graph")
        self.assertEqual(res.status_code, 200)

    def test_api_state(self):
        res = self.client.get("/api/state")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("stakeholders", data)
        self.assertIn("interactions", data)

    def test_api_create_stakeholder(self):
        payload = {
            "name": "Jordan Bell",
            "role": "VP Operations",
            "organization": "Meridian Systems",
            "tier": "vp",
            "goals": ["Scale infrastructure"],
            "vulnerabilities": ["Risk averse"]
        }
        res = self.client.post("/api/stakeholder", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["stakeholder"]["name"], "Jordan Bell")

    def test_api_create_interaction(self):
        # Pick two existing stakeholders
        sids = list(app.view_functions.keys())
        res_state = self.client.get("/api/state").get_json()
        all_sids = list(res_state["stakeholders"].keys())
        self.assertGreaterEqual(len(all_sids), 2)
        src, tgt = all_sids[0], all_sids[1]

        payload = {
            "source_id": src,
            "target_id": tgt,
            "type": "negotiation",
            "sentiment": 1,
            "summary": "Agreed on terms for Q3 resource allocation",
            "commitments_made": ["Provide weekly sync updates"]
        }
        res = self.client.post("/api/interaction", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("relationship_forward", data)

    def test_api_advisor_briefing_builtin(self):
        res_state = self.client.get("/api/state").get_json()
        first_sid = list(res_state["stakeholders"].keys())[0]

        payload = {
            "stakeholder_id": first_sid,
            "context": "Preparation for board alignment sync",
            "provider": "builtin"
        }
        res = self.client.post("/api/advisor/briefing", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("output", data)
        self.assertEqual(data.get("provider"), "builtin")
        self.assertIn("Executive Strategic Briefing", data["output"])


if __name__ == "__main__":
    unittest.main()
