from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
import math

class MoveType(Enum):
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
    type: str
    value: str
    confidence: float
    source_span: tuple

@dataclass
class Interpretation:
    id: str
    description: str
    intent: str
    entities: List[str]
    plausibility: float
    risk_score: float

@dataclass
class ConversationState:
    """Definition 1.1: State Vector S_t with Goal Stack."""
    topic: str = "general"
    entities: Dict[str, Any] = field(default_factory=dict)

    # G: Goal Distribution -> Now a Stack for context retention
    goal_stack: List[str] = field(default_factory=list)
    active_goal: Optional[str] = None

    posture: str = "neutral"
    trust: float = 0.5
    explicitness: float = 0.5
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
            "trust": self.trust
        }

@dataclass
class ULEOutput:
    move: MoveType
    rationale: str
    selected_interpretation: Optional[Interpretation]
    response_content: str
