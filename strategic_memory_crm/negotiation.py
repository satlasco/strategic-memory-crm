"""Negotiation pattern analysis.

Classifies stakeholders by their negotiation behavior and detects
recurring patterns like serial concession-makers, escalators,
and reciprocal traders.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CRMState, Interaction


@dataclass
class NegotiationProfile:
    """Behavioral profile for a stakeholder's negotiation history."""

    stakeholder_id: str = ""
    total_negotiations: int = 0
    concessions_made: int = 0
    concessions_received: int = 0
    power_moves: int = 0
    commitments_made: int = 0
    commitments_kept: int = 0
    commitments_broken: int = 0
    avg_sentiment: float = 0.0
    dominant_style: str = "unknown"
    patterns: list[str] = field(default_factory=list)

    @property
    def reliability_score(self) -> float:
        if self.commitments_made == 0:
            return 0.5
        return self.commitments_kept / self.commitments_made

    @property
    def concession_ratio(self) -> float:
        total = self.concessions_made + self.concessions_received
        if total == 0:
            return 0.5
        return self.concessions_made / total

    def to_dict(self) -> dict:
        return {
            "stakeholder_id": self.stakeholder_id,
            "total_negotiations": self.total_negotiations,
            "concessions_made": self.concessions_made,
            "concessions_received": self.concessions_received,
            "power_moves": self.power_moves,
            "commitments_made": self.commitments_made,
            "commitments_kept": self.commitments_kept,
            "commitments_broken": self.commitments_broken,
            "avg_sentiment": round(self.avg_sentiment, 3),
            "reliability_score": round(self.reliability_score, 3),
            "concession_ratio": round(self.concession_ratio, 3),
            "dominant_style": self.dominant_style,
            "patterns": self.patterns,
        }


STYLE_LABELS = {
    "dominator": "Uses power plays frequently, rarely concedes",
    "accommodator": "Concedes often, avoids confrontation",
    "collaborator": "Balanced give-and-take, builds joint value",
    "competitor": "Pushes for advantage, moderate concessions",
    "avoider": "Low engagement in negotiations",
}


def _classify_style(profile: NegotiationProfile) -> str:
    if profile.total_negotiations < 2:
        return "unknown"
    if profile.power_moves > profile.total_negotiations * 0.4:
        return "dominator"
    if profile.concession_ratio > 0.7:
        return "accommodator"
    if 0.35 <= profile.concession_ratio <= 0.65 and profile.reliability_score > 0.7:
        return "collaborator"
    if profile.concession_ratio < 0.3:
        return "competitor"
    return "collaborator"


def _detect_patterns(profile: NegotiationProfile) -> list[str]:
    patterns: list[str] = []
    if profile.reliability_score < 0.4 and profile.commitments_made >= 3:
        patterns.append("serial_promise_breaker")
    if profile.reliability_score > 0.85 and profile.commitments_made >= 3:
        patterns.append("highly_reliable")
    if profile.power_moves >= 3 and profile.concessions_made == 0:
        patterns.append("pure_escalator")
    if profile.concessions_made >= 4 and profile.power_moves == 0:
        patterns.append("chronic_yielder")
    if profile.avg_sentiment < -0.5:
        patterns.append("antagonistic_negotiator")
    if profile.avg_sentiment > 1.0:
        patterns.append("rapport_builder")
    return patterns


def build_negotiation_profile(state: CRMState, stakeholder_id: str) -> NegotiationProfile:
    """Analyze all negotiations involving a stakeholder."""
    interactions = state.get_stakeholder_interactions(stakeholder_id)
    negotiations = [i for i in interactions if i.type.value in ("negotiation", "conflict")]

    profile = NegotiationProfile(stakeholder_id=stakeholder_id)
    profile.total_negotiations = len(negotiations)

    sentiments: list[int] = []
    for neg in negotiations:
        sentiments.append(neg.sentiment.value)
        if neg.concession_made:
            if neg.initiator == stakeholder_id:
                profile.concessions_made += 1
            else:
                profile.concessions_received += 1
        if neg.power_move:
            if neg.initiator == stakeholder_id:
                profile.power_moves += 1
        if neg.commitments_made:
            profile.commitments_made += len(neg.commitments_made)
            if neg.commitments_kept is True:
                profile.commitments_kept += len(neg.commitments_made)
            elif neg.commitments_kept is False:
                profile.commitments_broken += len(neg.commitments_made)

    profile.avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    profile.dominant_style = _classify_style(profile)
    profile.patterns = _detect_patterns(profile)
    return profile


def build_all_profiles(state: CRMState) -> dict[str, NegotiationProfile]:
    """Return negotiation profiles for every stakeholder."""
    return {
        sid: build_negotiation_profile(state, sid)
        for sid in state.stakeholders
    }


def detect_reciprocal_pairs(state: CRMState) -> list[tuple[str, str, str]]:
    """Find pairs with notable reciprocal negotiation dynamics.

    Returns tuples of (stakeholder_a, stakeholder_b, dynamic_label).
    """
    profiles = build_all_profiles(state)
    pairs: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    for sid_a, prof_a in profiles.items():
        for sid_b, prof_b in profiles.items():
            if sid_a >= sid_b:
                continue
            key = (sid_a, sid_b)
            if key in seen:
                continue
            seen.add(key)

            if prof_a.dominant_style == "dominator" and prof_b.dominant_style == "accommodator":
                pairs.append((sid_a, sid_b, "power_imbalance"))
            elif prof_a.dominant_style == "accommodator" and prof_b.dominant_style == "dominator":
                pairs.append((sid_b, sid_a, "power_imbalance"))
            elif prof_a.dominant_style == "collaborator" and prof_b.dominant_style == "collaborator":
                pairs.append((sid_a, sid_b, "mutual_collaborators"))
            elif prof_a.dominant_style == "competitor" and prof_b.dominant_style == "competitor":
                pairs.append((sid_a, sid_b, "competitive_deadlock"))

    return pairs
