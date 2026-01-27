from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
import math

# =============================================================================
# DEFINITIONS (Part I)
# =============================================================================

class MoveType(Enum):
    """The Conversational Move Algebra (Part IV)."""
    ACK = auto()           # Minimal response
    CLARIFY = auto()       # Reduce ambiguity
    ANSWER = auto()        # Provide information
    EXPLAIN = auto()       # Answer + reasoning
    PROPOSE = auto()       # Suggest action
    REFUSE = auto()        # Safe rejection
    SUMMARIZE = auto()     # Compression
    META = auto()          # Talk about conversation

@dataclass
class SemanticAnchor:
    """Definition 3.1: Semantic Anchors"""
    type: str # 'entity', 'predicate', 'temporal'
    value: str
    confidence: float
    source_span: tuple # (start, end) in text

@dataclass
class Interpretation:
    """Definition 1.3: Single Hypothesis h_i"""
    id: str
    description: str
    intent: str
    entities: List[str]
    plausibility: float # p(h)
    risk_score: float   # risk(h)

@dataclass
class ConversationState:
    """Definition 1.1: State Vector S_t"""
    # T: Topic Manifold (Simplified as current topic string for V1)
    topic: str = "general"

    # E: Entity Grounding
    entities: Dict[str, Any] = field(default_factory=dict)

    # G: Goal Distribution (Simplified as active goal)
    active_goal: Optional[str] = None

    # P: Posture
    posture: str = "neutral"

    # Tau: Trust Scalar [0,1] (Theorem 2.3/2.4)
    trust: float = 0.5

    # Epsilon: Explicitness Scalar [0,1] (Theorem 2.5)
    explicitness: float = 0.5

    # Delta: Unresolved Gaps
    unresolved_gaps: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "topic": self.topic,
            "trust": self.trust,
            "explicitness": self.explicitness,
            "gaps": len(self.unresolved_gaps)
        }

@dataclass
class ULEOutput:
    move: MoveType
    rationale: str
    selected_interpretation: Optional[Interpretation]
    response_content: str
