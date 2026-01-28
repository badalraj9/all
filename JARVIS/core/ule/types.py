from typing import List, Dict, Set, Optional, Literal, Union, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# =============================================================================
# PART I: FOUNDATIONAL DEFINITIONS
# =============================================================================

# -- T: Topic Manifold --
class Topic(BaseModel):
    name: str
    embedding: List[float] = Field(default_factory=list)
    confidence: float = 1.0

# -- E: Entity Grounding --
class Entity(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    grounded_at: datetime = Field(default_factory=datetime.now)

# -- G: Goal Distribution --
class Goal(BaseModel):
    id: str
    description: str
    priority: float  # [0, 1]
    status: Literal['active', 'completed', 'failed', 'dormant'] = 'active'

# -- P: Posture --
class Posture(str, Enum):
    NEUTRAL = "neutral"
    ASSERTIVE = "assertive"
    INQUISITIVE = "inquisitive"
    APOLOGETIC = "apologetic"
    ENTHUSIASTIC = "enthusiastic"

# -- Δ: Unresolved Gaps --
class Gap(BaseModel):
    id: str
    description: str
    type: Literal['ambiguity', 'missing_info', 'conflict']
    severity: float  # [0, 1]

# -- S: Conversation State --
class ConversationState(BaseModel):
    # Core Components S = (T, E, G, P, τ, ε, Δ)
    topic: Topic
    entities: List[Entity] = Field(default_factory=list)
    goals: List[Goal] = Field(default_factory=list)
    posture: Posture = Posture.NEUTRAL
    trust: float = 0.5  # τ: Trust scalar [0, 1]
    explicitness: float = 0.5  # ε: Explicitness scalar [0, 1]
    gaps: List[Gap] = Field(default_factory=list)  # Δ

    # Metadata
    turn_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

# =============================================================================
# PART II: INTERPRETATION SPACE
# =============================================================================

class Hypothesis(BaseModel):
    id: str
    content: str  # The interpretation
    confidence: float  # p(h)
    reasoning: str
    required_entities: List[str] = Field(default_factory=list)
    implied_goal: Optional[str] = None
    risk_assessment: Optional['Risk'] = None

# =============================================================================
# PART III: MOVE ALGEBRA
# =============================================================================

class MoveType(str, Enum):
    ACK = "ACK"
    CLARIFY = "CLARIFY"
    ANSWER = "ANSWER"
    EXPLAIN = "EXPLAIN"
    PROPOSE = "PROPOSE"
    REFUSE = "REFUSE"
    SUMMARIZE = "SUMMARIZE"
    META = "META"

class Move(BaseModel):
    type: MoveType
    content: str
    rationale: str
    target_hypothesis_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# PART IV: RISK & COST
# =============================================================================

class Risk(BaseModel):
    score: float  # [0, 1]
    factors: List[str] = Field(default_factory=list)
    is_safe: bool

class Anchors(BaseModel):
    entities: List[str]
    intent_keywords: List[str]
    temporal_markers: List[str]
    raw_text: str
