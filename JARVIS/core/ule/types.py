from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
import math

# =============================================================================
# PART I: MATHEMATICAL FOUNDATION
# =============================================================================

class MoveType(Enum):
    """The Finite Move Algebra M (Theorem 4.1)."""
    ACK = auto()
    CLARIFY = auto()
    ANSWER = auto()
    EXPLAIN = auto()
    PROPOSE = auto()
    REFUSE = auto()
    SUMMARIZE = auto()
    META = auto()

@dataclass
class SemanticAnchor:
    """Raw semantic evidence extracted from input."""
    type: str # 'entity', 'predicate', 'reference', 'temporal'
    value: str
    confidence: float
    source_span: tuple

@dataclass
class Interpretation:
    """Definition 1.3: A structured Hypothesis h ∈ H."""
    id: str
    description: str
    intent: str
    entities: List[str]
    plausibility: float # p(h)
    risk_score: float   # risk(h)

@dataclass
class ConversationState:
    """
    Definition 1.1: Conversation State Vector S_t
    S = (T, E, G, P, τ, ε, Δ)
    """
    # T: Topic Manifold (Simplified as string/vector placeholder)
    topic: str = "general"

    # E: Entity Grounding (Symbol table)
    entities: Dict[str, Any] = field(default_factory=dict)

    # G: Goal Distribution (Implemented as Stack for context)
    goal_stack: List[str] = field(default_factory=list)
    active_goal: Optional[str] = None

    # P: Posture (Discrete set)
    posture: str = "neutral"

    # τ: Trust Scalar [0,1] (Theorem 2.4)
    trust: float = 0.5

    # ε: Explicitness Scalar [0,1] (Theorem 2.5)
    explicitness: float = 0.5

    # Δ: Unresolved Gaps (Set)
    unresolved_gaps: List[str] = field(default_factory=list)

    def push_goal(self, goal: str):
        if self.active_goal:
            self.goal_stack.append(self.active_goal)
        self.active_goal = goal

    def pop_goal(self):
        if self.goal_stack:
            self.active_goal = self.goal_stack.pop()
        else:
            self.active_goal = None

    def to_dict(self):
        return {
            "topic": self.topic,
            "active_goal": self.active_goal,
            "stack_depth": len(self.goal_stack),
            "trust": self.trust,
            "explicitness": self.explicitness,
            "gaps": len(self.unresolved_gaps)
        }

@dataclass
class ULEOutput:
    """The result of f(S, U) -> (Move, Response)."""
    move: MoveType
    rationale: str
    selected_interpretation: Optional[Interpretation]
    response_content: str
