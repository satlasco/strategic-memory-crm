"""Trust dynamics engine.

Models trust as a continuous signal shaped by interaction history,
commitment follow-through, reciprocity, and personality compatibility.
Trust is asymmetric: A's trust in B may differ from B's trust in A.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CRMState, Interaction, Relationship, Stakeholder


# --- Tunable constants ---------------------------------------------------

TRUST_FLOOR = 0.0
TRUST_CEILING = 1.0
DECAY_RATE = 0.005          # daily passive decay toward neutral (0.5)
BETRAYAL_PENALTY = 0.25
COMMITMENT_KEPT_BONUS = 0.08
COMMITMENT_BROKEN_PENALTY = 0.15
SENTIMENT_WEIGHT = 0.04
RECIPROCITY_FACTOR = 0.03
PERSONALITY_COMPAT_WEIGHT = 0.02


def _clamp(val: float) -> float:
    return max(TRUST_FLOOR, min(TRUST_CEILING, val))


def personality_compatibility(a: Stakeholder, b: Stakeholder) -> float:
    """Return [-1, 1] compatibility score based on personality overlap."""
    axes = set(a.personality.keys()) | set(b.personality.keys())
    if not axes:
        return 0.0
    diffs = [abs(a.personality.get(ax, 0.5) - b.personality.get(ax, 0.5)) for ax in axes]
    avg_diff = sum(diffs) / len(diffs)
    return 1.0 - 2.0 * avg_diff  # 0 diff -> 1.0, 0.5 diff -> 0.0


def apply_interaction(rel: Relationship, interaction: Interaction,
                      source: Stakeholder, target: Stakeholder) -> float:
    """Update trust score on *rel* given a new interaction. Returns delta."""
    delta = 0.0

    # Sentiment contribution
    delta += interaction.sentiment.value * SENTIMENT_WEIGHT

    # Commitment follow-through
    if interaction.commitments_kept is True:
        delta += COMMITMENT_KEPT_BONUS
    elif interaction.commitments_kept is False:
        delta -= COMMITMENT_BROKEN_PENALTY

    # Betrayal
    if interaction.type.value == "betrayal":
        delta -= BETRAYAL_PENALTY

    # Favors boost trust
    if interaction.type.value == "favor":
        delta += 0.06

    # Reciprocity adjustment
    if interaction.initiator == rel.source_id:
        rel.reciprocity_balance += 0.1
    elif interaction.initiator == rel.target_id:
        rel.reciprocity_balance -= 0.1
    imbalance = abs(rel.reciprocity_balance)
    delta -= imbalance * RECIPROCITY_FACTOR

    # Personality compatibility nudge
    compat = personality_compatibility(source, target)
    delta += compat * PERSONALITY_COMPAT_WEIGHT

    # Explicit trust_delta override from interaction data
    delta += interaction.trust_delta

    old = rel.trust_score
    rel.trust_score = _clamp(rel.trust_score + delta)
    rel.interaction_count += 1
    rel.sentiment_history.append(interaction.sentiment.value)
    rel.last_interaction = interaction.timestamp

    return rel.trust_score - old


def passive_decay(rel: Relationship, days_elapsed: int) -> float:
    """Apply time-based trust regression toward 0.5 (neutral)."""
    if days_elapsed <= 0:
        return 0.0
    direction = 0.5 - rel.trust_score
    magnitude = DECAY_RATE * days_elapsed * abs(direction)
    shift = math.copysign(magnitude, direction)
    old = rel.trust_score
    rel.trust_score = _clamp(rel.trust_score + shift)
    return rel.trust_score - old


def compute_trust_trajectory(rel: Relationship) -> str:
    """Classify the trust trend over the last N sentiment observations."""
    hist = rel.sentiment_history[-10:]
    if len(hist) < 3:
        return "insufficient_data"
    first_half = sum(hist[: len(hist) // 2]) / (len(hist) // 2)
    second_half = sum(hist[len(hist) // 2 :]) / (len(hist) - len(hist) // 2)
    diff = second_half - first_half
    if diff > 0.4:
        return "improving"
    if diff < -0.4:
        return "deteriorating"
    return "stable"


def rebuild_trust_scores(state: CRMState) -> None:
    """Re-derive every relationship's trust score from interaction history."""
    for rel in state.relationships.values():
        rel.trust_score = 0.5
        rel.reciprocity_balance = 0.0
        rel.sentiment_history = []
        rel.interaction_count = 0

    for interaction in sorted(state.interactions, key=lambda i: i.timestamp):
        for pid in interaction.participants:
            for other in interaction.participants:
                if pid == other:
                    continue
                rel = state.get_or_create_relationship(pid, other)
                src = state.stakeholders.get(pid)
                tgt = state.stakeholders.get(other)
                if src and tgt:
                    apply_interaction(rel, interaction, src, tgt)
