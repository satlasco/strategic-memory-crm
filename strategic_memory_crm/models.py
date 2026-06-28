"""Core data models for stakeholders, interactions, and relationships."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PersonalityAxis(Enum):
    """Big-Five-inspired personality axes relevant to professional dynamics."""

    ASSERTIVENESS = "assertiveness"
    OPENNESS = "openness"
    AGREEABLENESS = "agreeableness"
    CONSCIENTIOUSNESS = "conscientiousness"
    POLITICAL_SAVVY = "political_savvy"


class InteractionType(Enum):
    """Categories of stakeholder interactions."""

    MEETING = "meeting"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    NEGOTIATION = "negotiation"
    SOCIAL = "social"
    CONFLICT = "conflict"
    FAVOR = "favor"
    BETRAYAL = "betrayal"
    INTRODUCTION = "introduction"
    COLLABORATION = "collaboration"


class Sentiment(Enum):
    """Interaction sentiment from the observer's perspective."""

    VERY_POSITIVE = 2
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1
    VERY_NEGATIVE = -2


class OrgTier(Enum):
    """Organizational hierarchy tiers."""

    C_SUITE = "c_suite"
    VP = "vp"
    DIRECTOR = "director"
    MANAGER = "manager"
    INDIVIDUAL = "individual"
    EXTERNAL = "external"


@dataclass
class Stakeholder:
    """A person in the relationship network."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    role: str = ""
    organization: str = ""
    tier: OrgTier = OrgTier.INDIVIDUAL
    personality: dict[str, float] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    vulnerabilities: list[str] = field(default_factory=list)
    allies: list[str] = field(default_factory=list)
    rivals: list[str] = field(default_factory=list)
    active: bool = True

    def personality_score(self, axis: PersonalityAxis) -> float:
        return self.personality.get(axis.value, 0.5)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "organization": self.organization,
            "tier": self.tier.value,
            "personality": self.personality,
            "goals": self.goals,
            "vulnerabilities": self.vulnerabilities,
            "allies": self.allies,
            "rivals": self.rivals,
            "active": self.active,
        }


@dataclass
class Interaction:
    """A recorded interaction between stakeholders."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = ""
    type: InteractionType = InteractionType.MEETING
    participants: list[str] = field(default_factory=list)
    initiator: str = ""
    sentiment: Sentiment = Sentiment.NEUTRAL
    trust_delta: float = 0.0
    influence_shift: float = 0.0
    summary: str = ""
    context: str = ""
    commitments_made: list[str] = field(default_factory=list)
    commitments_kept: Optional[bool] = None
    power_move: bool = False
    concession_made: bool = False
    information_shared: list[str] = field(default_factory=list)
    information_withheld: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.type.value,
            "participants": self.participants,
            "initiator": self.initiator,
            "sentiment": self.sentiment.value,
            "trust_delta": self.trust_delta,
            "influence_shift": self.influence_shift,
            "summary": self.summary,
            "context": self.context,
            "commitments_made": self.commitments_made,
            "commitments_kept": self.commitments_kept,
            "power_move": self.power_move,
            "concession_made": self.concession_made,
            "information_shared": self.information_shared,
            "information_withheld": self.information_withheld,
        }


@dataclass
class Relationship:
    """A directed edge between two stakeholders with evolving dynamics."""

    source_id: str = ""
    target_id: str = ""
    trust_score: float = 0.5
    influence_weight: float = 0.0
    reciprocity_balance: float = 0.0
    interaction_count: int = 0
    last_interaction: str = ""
    sentiment_history: list[int] = field(default_factory=list)
    negotiation_style: str = "collaborative"
    risk_level: float = 0.0
    entropy_score: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "trust_score": round(self.trust_score, 3),
            "influence_weight": round(self.influence_weight, 3),
            "reciprocity_balance": round(self.reciprocity_balance, 3),
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction,
            "sentiment_history": self.sentiment_history,
            "negotiation_style": self.negotiation_style,
            "risk_level": round(self.risk_level, 3),
            "entropy_score": round(self.entropy_score, 3),
            "notes": self.notes,
        }


@dataclass
class CRMState:
    """Top-level state container for the entire CRM."""

    stakeholders: dict[str, Stakeholder] = field(default_factory=dict)
    interactions: list[Interaction] = field(default_factory=list)
    relationships: dict[tuple[str, str], Relationship] = field(default_factory=dict)

    def add_stakeholder(self, s: Stakeholder) -> None:
        self.stakeholders[s.id] = s

    def add_interaction(self, i: Interaction) -> None:
        self.interactions.append(i)

    def get_or_create_relationship(self, src: str, tgt: str) -> Relationship:
        key = (src, tgt)
        if key not in self.relationships:
            self.relationships[key] = Relationship(source_id=src, target_id=tgt)
        return self.relationships[key]

    def get_stakeholder_interactions(self, sid: str) -> list[Interaction]:
        return [i for i in self.interactions if sid in i.participants]

    def get_stakeholder_relationships(self, sid: str) -> list[Relationship]:
        return [r for r in self.relationships.values() if r.source_id == sid or r.target_id == sid]

    def to_dict(self) -> dict:
        return {
            "stakeholders": {k: v.to_dict() for k, v in self.stakeholders.items()},
            "interactions": [i.to_dict() for i in self.interactions],
            "relationships": [r.to_dict() for r in self.relationships.values()],
        }
