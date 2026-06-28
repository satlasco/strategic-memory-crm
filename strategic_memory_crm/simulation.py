"""Interaction history simulator.

Generates plausible interaction sequences between stakeholders
based on their roles, personality profiles, existing relationships,
and organizational dynamics.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CRMState

from .models import Interaction, InteractionType, Sentiment


def simulate_interactions(
    state: CRMState,
    n_interactions: int = 50,
    start_date: str = "2024-01-15",
    seed: int | None = 42,
) -> list[Interaction]:
    """Generate a realistic sequence of interactions between stakeholders."""
    if seed is not None:
        random.seed(seed)

    sids = list(state.stakeholders.keys())
    if len(sids) < 2:
        return []

    base_date = datetime.fromisoformat(start_date)
    interactions: list[Interaction] = []

    for i in range(n_interactions):
        ts = base_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59),
        )

        # Weighted participant selection: allies interact more, rivals conflict
        initiator = random.choice(sids)
        s_init = state.stakeholders[initiator]

        target_pool = [s for s in sids if s != initiator]
        weights = []
        for t in target_pool:
            w = 1.0
            if t in s_init.allies:
                w += 2.0
            if t in s_init.rivals:
                w += 1.5  # rivals also interact, but differently
            if state.stakeholders[t].organization == s_init.organization:
                w += 1.0
            weights.append(w)

        target = random.choices(target_pool, weights=weights, k=1)[0]
        s_tgt = state.stakeholders[target]

        # Determine interaction type based on relationship
        is_rival = target in s_init.rivals or initiator in s_tgt.rivals
        is_ally = target in s_init.allies or initiator in s_tgt.allies

        if is_rival:
            itype = random.choices(
                [InteractionType.NEGOTIATION, InteractionType.CONFLICT,
                 InteractionType.MEETING, InteractionType.EMAIL],
                weights=[3, 2, 2, 1], k=1
            )[0]
        elif is_ally:
            itype = random.choices(
                [InteractionType.COLLABORATION, InteractionType.MEETING,
                 InteractionType.FAVOR, InteractionType.SOCIAL,
                 InteractionType.EMAIL],
                weights=[3, 2, 2, 1, 1], k=1
            )[0]
        else:
            itype = random.choices(
                [InteractionType.MEETING, InteractionType.EMAIL,
                 InteractionType.PHONE_CALL, InteractionType.NEGOTIATION,
                 InteractionType.SOCIAL, InteractionType.COLLABORATION],
                weights=[3, 2, 2, 1, 1, 1], k=1
            )[0]

        # Sentiment
        if itype in (InteractionType.CONFLICT, InteractionType.BETRAYAL):
            sent = random.choices(
                [Sentiment.VERY_NEGATIVE, Sentiment.NEGATIVE, Sentiment.NEUTRAL],
                weights=[3, 4, 1], k=1
            )[0]
        elif itype in (InteractionType.FAVOR, InteractionType.COLLABORATION):
            sent = random.choices(
                [Sentiment.VERY_POSITIVE, Sentiment.POSITIVE, Sentiment.NEUTRAL],
                weights=[2, 4, 1], k=1
            )[0]
        elif itype == InteractionType.NEGOTIATION:
            sent = random.choices(
                list(Sentiment), weights=[1, 2, 3, 2, 1], k=1
            )[0]
        else:
            sent = random.choices(
                list(Sentiment), weights=[1, 3, 4, 1, 0], k=1
            )[0]

        # Trust delta
        trust_delta = sent.value * random.uniform(0.01, 0.05)

        # Commitments
        commitments: list[str] = []
        commitments_kept = None
        if itype in (InteractionType.NEGOTIATION, InteractionType.MEETING, InteractionType.COLLABORATION):
            if random.random() < 0.4:
                commitment_templates = [
                    "Deliver revised proposal by next week",
                    "Share internal analysis data",
                    "Set up follow-up meeting with leadership",
                    "Provide budget estimates",
                    "Introduce to key decision-maker",
                    "Review contract terms",
                    "Align teams on project timeline",
                    "Secure executive sponsorship",
                ]
                commitments = random.sample(commitment_templates, k=random.randint(1, 2))
                reliability = s_init.personality.get("conscientiousness", 0.5)
                commitments_kept = random.random() < (reliability * 0.8 + 0.1)

        # Power moves and concessions
        power_move = False
        concession = False
        if itype == InteractionType.NEGOTIATION:
            assertiveness = s_init.personality.get("assertiveness", 0.5)
            power_move = random.random() < assertiveness * 0.5
            agreeableness = s_init.personality.get("agreeableness", 0.5)
            concession = random.random() < agreeableness * 0.4

        # Information dynamics
        info_shared: list[str] = []
        info_withheld: list[str] = []
        if random.random() < 0.3:
            info_pool = [
                "Q3 revenue projections", "Org restructuring plans",
                "Competitor intelligence", "Budget allocation changes",
                "Personnel changes", "Strategic pivot considerations",
                "Client satisfaction data", "Technology migration timeline",
            ]
            shared_count = random.randint(1, 2)
            withheld_count = random.randint(0, 1)
            selected = random.sample(info_pool, k=min(shared_count + withheld_count, len(info_pool)))
            info_shared = selected[:shared_count]
            info_withheld = selected[shared_count:shared_count + withheld_count]

        # Occasional betrayals in rival relationships
        if is_rival and random.random() < 0.08:
            itype = InteractionType.BETRAYAL
            sent = Sentiment.VERY_NEGATIVE
            trust_delta = -0.15

        summary = _generate_summary(itype, s_init.name, s_tgt.name, sent)

        interaction = Interaction(
            timestamp=ts.isoformat(),
            type=itype,
            participants=[initiator, target],
            initiator=initiator,
            sentiment=sent,
            trust_delta=trust_delta,
            summary=summary,
            context=f"{s_init.organization} <-> {s_tgt.organization}",
            commitments_made=commitments,
            commitments_kept=commitments_kept,
            power_move=power_move,
            concession_made=concession,
            information_shared=info_shared,
            information_withheld=info_withheld,
        )
        interactions.append(interaction)

    interactions.sort(key=lambda x: x.timestamp)
    for inter in interactions:
        state.add_interaction(inter)

    return interactions


_SUMMARIES: dict[str, list[str]] = {
    "meeting": [
        "{a} and {b} held a strategy alignment session",
        "{a} presented quarterly roadmap to {b}",
        "{a} and {b} discussed project milestones",
        "{a} briefed {b} on cross-functional dependencies",
    ],
    "email": [
        "{a} sent status update to {b}",
        "{a} shared documentation with {b}",
        "{a} followed up on action items with {b}",
    ],
    "phone_call": [
        "{a} called {b} to discuss urgent timeline changes",
        "{a} and {b} had a quick sync call",
    ],
    "negotiation": [
        "{a} and {b} negotiated resource allocation terms",
        "{a} proposed revised deal structure to {b}",
        "{a} and {b} debated project ownership boundaries",
    ],
    "social": [
        "{a} and {b} had lunch together",
        "{a} attended {b}'s team celebration",
    ],
    "conflict": [
        "{a} raised concerns about {b}'s team performance",
        "{a} and {b} disagreed on strategic direction",
        "Tension between {a} and {b} surfaced in leadership meeting",
    ],
    "favor": [
        "{a} helped {b} with a critical deadline",
        "{a} introduced {b} to a valuable contact",
        "{a} advocated for {b}'s proposal in board meeting",
    ],
    "betrayal": [
        "{a} shared {b}'s confidential information with leadership",
        "{a} undermined {b}'s position in stakeholder meeting",
    ],
    "introduction": [
        "{a} introduced {b} to key external partners",
    ],
    "collaboration": [
        "{a} and {b} co-authored the integration proposal",
        "{a} and {b} jointly presented to the steering committee",
        "{a} and {b} aligned on shared KPIs",
    ],
}


def _generate_summary(itype: InteractionType, name_a: str, name_b: str,
                       sentiment: Sentiment) -> str:
    templates = _SUMMARIES.get(itype.value, ["{a} interacted with {b}"])
    template = random.choice(templates)
    base = template.format(a=name_a, b=name_b)
    if sentiment.value <= -2:
        base += " — ended on hostile terms"
    elif sentiment.value >= 2:
        base += " — strong rapport established"
    return base
