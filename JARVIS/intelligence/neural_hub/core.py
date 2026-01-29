import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

# =============================================================================
# CONSTANTS & PATTERNS
# =============================================================================

DECISION_PATTERNS = [
    {"name": "decided", "pattern": r"\b(decided|decision)\b", "baseWeight": 2.0},
    {"name": "lets_go_with", "pattern": r"let'?s go with", "baseWeight": 2.5},
    {"name": "will_use", "pattern": r"we('|ll)? use", "baseWeight": 1.5},
    {"name": "final", "pattern": r"final(ized?)?", "baseWeight": 1.8},
    {"name": "settled_on", "pattern": r"settled on", "baseWeight": 2.2},
    {"name": "agreed", "pattern": r"agreed", "baseWeight": 1.2},
    {"name": "pick", "pattern": r"\b(pick|choose|chose)\b", "baseWeight": 1.0},
]

DEFAULT_THRESHOLD = 0.75

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Signal:
    name: str
    type: str # linguistic, structural, contextual, temporal
    value: float
    baseWeight: float

@dataclass
class NeuralState:
    user_id: str
    project_id: str
    weights: Dict[str, float] = field(default_factory=dict)
    threshold: float = DEFAULT_THRESHOLD
    alpha: float = 1.0 # Beta distribution alpha (accepts)
    beta: float = 1.0  # Beta distribution beta (rejects)

@dataclass
class ProcessingContext:
    chat_type: str = "direct"
    is_author_maintainer: bool = False
    thread_depth: int = 0
    message_timestamp: float = 0.0

@dataclass
class ProcessResult:
    confidence: float
    should_propose: bool
    rationale: str
    signals: List[Dict[str, Any]]

# =============================================================================
# UTILS
# =============================================================================

def sigmoid(x: float, threshold: float, steepness: float = 10.0) -> float:
    """
    Sigmoid activation function tailored for decision threshold.
    """
    return 1 / (1 + math.exp(-steepness * (x - threshold)))

# =============================================================================
# SENSORS
# =============================================================================

class LinguisticSensor:
    def extract(self, content: str) -> List[Signal]:
        signals = []
        for p in DECISION_PATTERNS:
            if re.search(p["pattern"], content, re.IGNORECASE):
                signals.append(Signal(
                    name=p["name"],
                    type="linguistic",
                    value=1.0,
                    baseWeight=p["baseWeight"]
                ))
        return signals

class StructuralSensor:
    def extract(self, ctx: ProcessingContext) -> List[Signal]:
        signals = []
        # Thread depth signal
        depth_value = min(ctx.thread_depth * 0.03, 0.15)
        if depth_value > 0:
            signals.append(Signal(
                name="thread_depth",
                type="structural",
                value=depth_value,
                baseWeight=1.0
            ))

        if ctx.is_author_maintainer:
            signals.append(Signal(
                name="maintainer_author",
                type="structural",
                value=0.2,
                baseWeight=1.0
            ))
        return signals

# =============================================================================
# CORE ENGINE
# =============================================================================

class SynapticProcessor:
    def aggregate(self, signals: List[Signal], weights: Dict[str, float]) -> float:
        total = 0.0
        for signal in signals:
            w = weights.get(signal.name, signal.baseWeight)
            total += signal.value * w
        return total

    def activate(self, aggregated: float, threshold: float) -> float:
        return sigmoid(aggregated, threshold)

class NeuralHub:
    """
    Python Port of SENTRY Neural Hub.
    Deterministic Decision Intelligence.
    """
    def __init__(self):
        self.linguistic = LinguisticSensor()
        self.structural = StructuralSensor()
        self.processor = SynapticProcessor()

    def process(self, content: str, ctx: ProcessingContext, state: NeuralState) -> ProcessResult:
        # 1. Extract Signals
        signals = self.linguistic.extract(content)
        signals.extend(self.structural.extract(ctx))

        if not signals:
            return ProcessResult(0.0, False, "No decision signals detected", [])

        # 2. Aggregate
        aggregated = self.processor.aggregate(signals, state.weights)

        # 3. Activate
        confidence = self.processor.activate(aggregated, state.threshold)

        # 4. Decision
        should_propose = confidence >= 0.5

        # 5. Rationale
        rationale = f"Confidence: {confidence:.2f}. "
        if should_propose:
            rationale += "Signals suggest a decision."
        else:
            rationale += "Insufficient signal strength."

        return ProcessResult(
            confidence=confidence,
            should_propose=should_propose,
            rationale=rationale,
            signals=[{"name": s.name, "val": s.value} for s in signals]
        )

# Singleton
neural_hub = NeuralHub()
