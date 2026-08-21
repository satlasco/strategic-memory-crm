"""Storage and persistence utilities for Strategic Memory CRM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from strategic_memory_crm.models import (
    CRMState,
    Interaction,
    InteractionType,
    OrgTier,
    Relationship,
    Sentiment,
    Stakeholder,
)


def save_state_to_file(state: CRMState, filepath: Path | str) -> bool:
    """Saves CRMState to a JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "stakeholders": [s.to_dict() for s in state.stakeholders.values()],
        "interactions": [i.to_dict() for i in state.interactions],
        "relationships": [
            {
                "source_id": r.source_id,
                "target_id": r.target_id,
                "trust_score": r.trust_score,
                "influence_weight": r.influence_weight,
                "reciprocity_balance": r.reciprocity_balance,
                "interaction_count": r.interaction_count,
                "last_interaction": r.last_interaction,
                "sentiment_history": r.sentiment_history,
                "negotiation_style": r.negotiation_style,
                "risk_level": r.risk_level,
                "entropy_score": r.entropy_score,
                "notes": r.notes,
            }
            for r in state.relationships.values()
        ],
    }
    
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error saving state: {e}")
        return False


def load_state_from_file(filepath: Path | str) -> Optional[CRMState]:
    """Loads CRMState from a JSON file, or returns None if not found or corrupted."""
    path = Path(filepath)
    if not path.exists():
        return None
        
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        state = CRMState()
        
        # Load stakeholders
        for s_dict in data.get("stakeholders", []):
            tier_val = s_dict.get("tier", "individual")
            try:
                tier = OrgTier(tier_val)
            except ValueError:
                tier = OrgTier.INDIVIDUAL
                
            stk = Stakeholder(
                id=s_dict["id"],
                name=s_dict.get("name", ""),
                role=s_dict.get("role", ""),
                organization=s_dict.get("organization", ""),
                tier=tier,
                personality=s_dict.get("personality", {}),
                goals=s_dict.get("goals", []),
                vulnerabilities=s_dict.get("vulnerabilities", []),
                allies=s_dict.get("allies", []),
                rivals=s_dict.get("rivals", []),
                active=s_dict.get("active", True),
            )
            state.add_stakeholder(stk)
            
        # Load interactions
        for i_dict in data.get("interactions", []):
            try:
                itype = InteractionType(i_dict.get("type", "meeting"))
            except ValueError:
                itype = InteractionType.MEETING
                
            try:
                sent = Sentiment(i_dict.get("sentiment", 0))
            except ValueError:
                sent = Sentiment.NEUTRAL
                
            inter = Interaction(
                id=i_dict["id"],
                timestamp=i_dict.get("timestamp", ""),
                type=itype,
                participants=i_dict.get("participants", []),
                initiator=i_dict.get("initiator", ""),
                sentiment=sent,
                trust_delta=i_dict.get("trust_delta", 0.0),
                influence_shift=i_dict.get("influence_shift", 0.0),
                summary=i_dict.get("summary", ""),
                context=i_dict.get("context", ""),
                commitments_made=i_dict.get("commitments_made", []),
                commitments_kept=i_dict.get("commitments_kept"),
                power_move=i_dict.get("power_move", False),
                concession_made=i_dict.get("concession_made", False),
                information_shared=i_dict.get("information_shared", []),
                information_withheld=i_dict.get("information_withheld", []),
            )
            state.add_interaction(inter)
            
        # Load relationships
        for r_dict in data.get("relationships", []):
            src = r_dict["source_id"]
            tgt = r_dict["target_id"]
            rel = Relationship(
                source_id=src,
                target_id=tgt,
                trust_score=r_dict.get("trust_score", 0.5),
                influence_weight=r_dict.get("influence_weight", 0.0),
                reciprocity_balance=r_dict.get("reciprocity_balance", 0.0),
                interaction_count=r_dict.get("interaction_count", 0),
                last_interaction=r_dict.get("last_interaction", ""),
                sentiment_history=r_dict.get("sentiment_history", []),
                negotiation_style=r_dict.get("negotiation_style", "collaborative"),
                risk_level=r_dict.get("risk_level", 0.0),
                entropy_score=r_dict.get("entropy_score", 0.0),
                notes=r_dict.get("notes", []),
            )
            state.relationships[(src, tgt)] = rel
            
        return state
    except Exception as e:
        print(f"Error loading state: {e}")
        return None
