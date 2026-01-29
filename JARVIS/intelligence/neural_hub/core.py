import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# =============================================================================
# CONSTANTS & PATTERNS
# =============================================================================

# Comprehensive Pattern List (Future-Proofed)
DECISION_PATTERNS = [
    # --- EXPLICIT DECISIONS ---
    {"name": "decided", "pattern": r"\b(decided|decision)\b", "baseWeight": 2.5},
    {"name": "lets_go_with", "pattern": r"let'?s (go with|do|use|try)", "baseWeight": 2.5},
    {"name": "will_use", "pattern": r"we('|ll)? (use|adopt|implement)", "baseWeight": 2.0},
    {"name": "final", "pattern": r"final(ized?)?", "baseWeight": 2.0},
    {"name": "settled_on", "pattern": r"settled on", "baseWeight": 2.5},
    {"name": "agreed", "pattern": r"agreed", "baseWeight": 2.0},

    # --- SELECTION ---
    {"name": "pick", "pattern": r"\b(pick|choose|chose|select)\b", "baseWeight": 1.5},
    {"name": "prefer", "pattern": r"\b(prefer|leaning towards)\b", "baseWeight": 1.2},
    {"name": "option", "pattern": r"option [A-Z0-9]", "baseWeight": 1.5},

    # --- COMMANDS / INITIATION ---
    {"name": "start", "pattern": r"\b(start|begin|initiate|launch|commence)\b", "baseWeight": 2.2},
    {"name": "execute", "pattern": r"\b(execute|run|perform|do)\b", "baseWeight": 1.8},
    {"name": "create", "pattern": r"\b(create|make|build|generate|construct)\b", "baseWeight": 1.8},
    {"name": "research", "pattern": r"\b(research|investigate|analyze|study|look into)\b", "baseWeight": 2.0},

    # --- MODIFICATION / PIVOT ---
    {"name": "update", "pattern": r"\b(update|change|modify|revise|alter)\b", "baseWeight": 2.2},
    {"name": "focus", "pattern": r"\b(focus|target|prioritize|concentrate)\b", "baseWeight": 2.2},
    {"name": "switch", "pattern": r"\b(switch|pivot|shift)\b", "baseWeight": 2.0},
    {"name": "instead", "pattern": r"\b(instead|rather)\b", "baseWeight": 1.5},

    # --- CONFIRMATION ---
    {"name": "yes", "pattern": r"\b(yes|yeah|yep|sure|okay|ok|correct)\b", "baseWeight": 1.0},
    {"name": "confirm", "pattern": r"\b(confirm|approve|authorize|grant)\b", "baseWeight": 2.5},
    {"name": "proceed", "pattern": r"\b(proceed|continue|go ahead)\b", "baseWeight": 2.0},

    # --- URGENCY ---
    {"name": "now", "pattern": r"\b(now|immediately|asap|urgent)\b", "baseWeight": 0.5}, # modifier

    # --- NEGATION (Negative Weights) ---
    {"name": "maybe", "pattern": r"\b(maybe|perhaps|possibly|might)\b", "baseWeight": -1.0},
    {"name": "wait", "pattern": r"\b(wait|hold|pause)\b", "baseWeight": -2.0},
    {"name": "no", "pattern": r"\b(no|nope|nah|cancel|abort)\b", "baseWeight": -5.0},
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
