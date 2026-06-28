"""Relationship entropy scoring.

Entropy here measures the *unpredictability* of a relationship.
High entropy = volatile, hard-to-read dynamics.
Low entropy  = stable, predictable (for better or worse).

Uses Shannon entropy over discretized sentiment observations and
augments with variance in trust deltas and interaction regularity.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .models import CRMState, Relationship


@dataclass
class EntropyBreakdown:
    """Detailed entropy components for a relationship."""

    source_id: str = ""
    target_id: str = ""
    sentiment_entropy: float = 0.0
    trust_volatility: float = 0.0
    interaction_regularity: float = 0.0
    composite_entropy: float = 0.0
    risk_label: str = "stable"

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "sentiment_entropy": round(self.sentiment_entropy, 4),
            "trust_volatility": round(self.trust_volatility, 4),
            "interaction_regularity": round(self.interaction_regularity, 4),
            "composite_entropy": round(self.composite_entropy, 4),
            "risk_label": self.risk_label,
        }


def _shannon_entropy(values: list[int]) -> float:
    """Compute normalized Shannon entropy of a discrete distribution."""
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    n_classes = len(counts)
    if n_classes <= 1:
        return 0.0
    probs = [c / total for c in counts.values()]
    raw = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(n_classes)
    return raw / max_entropy if max_entropy > 0 else 0.0


def _trust_volatility(rel: Relationship, state: CRMState) -> float:
    """Measure variance in trust deltas across interactions."""
    interactions = [
        i for i in state.interactions
        if rel.source_id in i.participants and rel.target_id in i.participants
    ]
    if len(interactions) < 2:
        return 0.0
    deltas = [i.trust_delta + i.sentiment.value * 0.04 for i in interactions]
    return float(np.std(deltas))


def _interaction_regularity(rel: Relationship, state: CRMState) -> float:
    """Measure regularity of interaction timing (0 = very regular, 1 = erratic).

    Uses coefficient of variation of inter-interaction gaps.
    """
    interactions = sorted(
        [i for i in state.interactions
         if rel.source_id in i.participants and rel.target_id in i.participants],
        key=lambda i: i.timestamp,
    )
    if len(interactions) < 3:
        return 0.5  # not enough data
    # Parse timestamps and compute gaps in days
    from datetime import datetime
    timestamps = []
    for inter in interactions:
        try:
            timestamps.append(datetime.fromisoformat(inter.timestamp))
        except (ValueError, TypeError):
            continue
    if len(timestamps) < 3:
        return 0.5
    gaps = [(timestamps[i + 1] - timestamps[i]).total_seconds() / 86400
            for i in range(len(timestamps) - 1)]
    mean_gap = np.mean(gaps)
    if mean_gap == 0:
        return 0.0
    cv = float(np.std(gaps) / mean_gap)
    return min(1.0, cv)  # cap at 1.0


def compute_entropy(rel: Relationship, state: CRMState) -> EntropyBreakdown:
    """Compute composite relationship entropy."""
    breakdown = EntropyBreakdown(source_id=rel.source_id, target_id=rel.target_id)

    breakdown.sentiment_entropy = _shannon_entropy(rel.sentiment_history)
    breakdown.trust_volatility = _trust_volatility(rel, state)
    breakdown.interaction_regularity = _interaction_regularity(rel, state)

    # Weighted composite
    breakdown.composite_entropy = (
        0.45 * breakdown.sentiment_entropy
        + 0.35 * breakdown.trust_volatility
        + 0.20 * breakdown.interaction_regularity
    )

    # Risk label
    if breakdown.composite_entropy > 0.65:
        breakdown.risk_label = "volatile"
    elif breakdown.composite_entropy > 0.40:
        breakdown.risk_label = "uncertain"
    elif breakdown.composite_entropy > 0.20:
        breakdown.risk_label = "moderate"
    else:
        breakdown.risk_label = "stable"

    rel.entropy_score = breakdown.composite_entropy
    return breakdown


def compute_all_entropy(state: CRMState) -> list[EntropyBreakdown]:
    """Compute entropy for every active relationship."""
    results: list[EntropyBreakdown] = []
    for rel in state.relationships.values():
        if rel.interaction_count > 0:
            results.append(compute_entropy(rel, state))
    return results


def network_entropy(state: CRMState) -> float:
    """Aggregate entropy across the full relationship network."""
    breakdowns = compute_all_entropy(state)
    if not breakdowns:
        return 0.0
    return sum(b.composite_entropy for b in breakdowns) / len(breakdowns)
