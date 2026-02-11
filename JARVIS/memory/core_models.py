from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import uuid
import time
from enum import Enum
import json

class MemoryType(Enum):
    FACT = "fact"
    BELIEF = "belief"
    GOAL = "goal"
    CONSTRAINT = "constraint"

class RelationType(Enum):
    # Major Relations
    DEPENDS_ON = "depends_on"       # A depends on B
    CONTRADICTS = "contradicts"     # A conflicts with B
    CONTAINS = "contains"           # A includes B

    # Partial Relations
    RELATES_TO = "relates_to"       # A is relevant to B
    PREFERS = "prefers"             # User prefers A over B (if A is preference, B is option)
    ASSOCIATED_WITH = "associated_with" # Soft link

@dataclass
class TruthVector:
    """
    Mathematical representation of memory reliability.
    Assimilated from MemoryThread/tms_service.py
    """
    confidence: float  # 0.0 to 1.0: How certain are we?
    authority: float   # 0.0 to 1.0: How reliable is the source?
    freshness: float   # 0.0 to 1.0: Decay over time
    corroboration: float # 0.0 to 1.0: How many others agree?

    def to_score(self) -> float:
        """Calculate weighted truth score"""
        # Weights derived from MemoryThread defaults
        return (self.confidence * 0.4 +
                self.authority * 0.3 +
                self.freshness * 0.2 +
                self.corroboration * 0.1)

    def to_json(self) -> Dict:
        return {
            "confidence": self.confidence,
            "authority": self.authority,
            "freshness": self.freshness,
            "corroboration": self.corroboration
        }

@dataclass
class MemoryEvent:
    """
    An immutable record of something that happened or was thought.
    Mapped to the `events` table in Postgres.
    """
    id: str
    object_id: str  # The entity this event refers to
    actor: str
    action: str
    payload: Dict
    truth_vector: TruthVector
    timestamp: float
    antecedents: List[str]

    @staticmethod
    def create(actor: str, action: str, object_id: str, payload: Dict, confidence: float = 1.0, authority: float = 0.5):
        return MemoryEvent(
            id=str(uuid.uuid4()),
            object_id=object_id,
            actor=actor,
            action=action,
            payload=payload,
            truth_vector=TruthVector(confidence, authority, 1.0, 0.0),
            timestamp=time.time(),
            antecedents=[]
        )

@dataclass
class Relation:
    """
    A directed edge in the Context Web.
    """
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
