import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

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
    {"name": "restart", "pattern": r"\b(restart|reboot|resume)\b", "baseWeight": 2.5},
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

    # --- TERMINATION (Moved from Negation to Positive Command) ---
    {"name": "stop", "pattern": r"\b(stop|cancel|abort|terminate|end|halt)\b", "baseWeight": 4.0},
    {"name": "delete", "pattern": r"\b(delete|remove|erase|forget)\b", "baseWeight": 4.0},

    # --- URGENCY ---
    {"name": "now", "pattern": r"\b(now|immediately|asap|urgent)\b", "baseWeight": 0.5}, # modifier

    # --- NEGATION (Negative Weights) ---
    {"name": "maybe", "pattern": r"\b(maybe|perhaps|possibly|might)\b", "baseWeight": -1.0},
    {"name": "wait", "pattern": r"\b(wait|hold|pause)\b", "baseWeight": -2.0},
    {"name": "no", "pattern": r"\b(no|nope|nah)\b", "baseWeight": -2.0},
]

DEFAULT_THRESHOLD = 0.75

# =============================================================================
# DATA STRUCTURES
# =============================================================================

class ActivationMode(Enum):
    STANDARD = "sigmoid"       # Balanced
    STRICT = "steep_sigmoid"   # High confidence required
    EXPLORATORY = "softplus"   # Brainstorming

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
    alpha: float = 1.0
    beta: float = 1.0
    activation_mode: ActivationMode = ActivationMode.STANDARD

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
    detected_relations: List[Dict[str, str]] = field(default_factory=list)
    activation_used: str = "standard"

# =============================================================================
# UTILS
# =============================================================================

def sigmoid(x: float, threshold: float, steepness: float = 10.0) -> float:
    return 1 / (1 + math.exp(-steepness * (x - threshold)))

def softplus(x: float) -> float:
    # Tuned for Exploratory mode:
    # Dampen negatives heavily
    if x < 0: x = x * 0.1
    return math.log(1 + math.exp(x)) / 3.0 # High gain

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

    def activate_variable(self, aggregated: float, threshold: float, mode: ActivationMode) -> float:
        if mode == ActivationMode.STRICT:
            # Tuned: Higher threshold for Strict Mode
            strict_threshold = max(threshold, 0.85)
            return sigmoid(aggregated, strict_threshold, steepness=20.0)
        elif mode == ActivationMode.EXPLORATORY:
            val = softplus(aggregated)
            return min(val, 1.0)
        else:
            return sigmoid(aggregated, threshold, steepness=10.0)

class NeuralHub:
    def __init__(self):
        self.linguistic = LinguisticSensor()
        self.structural = StructuralSensor()
        self.processor = SynapticProcessor()

    def process(self, content: str, ctx: ProcessingContext, state: NeuralState, memory_system: Any = None) -> ProcessResult:
        signals = self.linguistic.extract(content)
        signals.extend(self.structural.extract(ctx))

        if not signals and state.activation_mode != ActivationMode.EXPLORATORY:
             return ProcessResult(0.0, False, "No decision signals detected", [], [], state.activation_mode.name)

        # STRICT MODE FILTERING: Ignore weak signals
        if state.activation_mode == ActivationMode.STRICT:
            signals = [s for s in signals if s.baseWeight >= 1.5]
            if not signals:
                return ProcessResult(0.0, False, "[STRICT] Signals too weak.", [], [], state.activation_mode.name)

        aggregated = self.processor.aggregate(signals, state.weights)

        # Override negative aggregates in exploratory mode
        if state.activation_mode == ActivationMode.EXPLORATORY and aggregated < 0:
             positives = sum(1 for s in signals if s.baseWeight > 0)
             if positives > 0:
                 aggregated = 0.5

        confidence = self.processor.activate_variable(aggregated, state.threshold, state.activation_mode)

        # Decision cutoff
        cutoff = 0.5
        if state.activation_mode == ActivationMode.EXPLORATORY: cutoff = 0.20 # Tuned to 0.20

        should_propose = confidence >= cutoff

        # --------------------------------------------------------------------------------
        # CONTEMPLATION LOOP (The Slow Path)
        # --------------------------------------------------------------------------------
        relations = []
        content_lower = content.lower()
        if should_propose and memory_system:
             # CALLING DEEP REASONING
             confidence = self.contemplate_deep(confidence, content, memory_system, relations)

             # Re-check cutoff
             if confidence < cutoff:
                  should_propose = False

        # Fallback Relation Detection (Fast Path)
        if should_propose and not relations:
            if "because" in content_lower or "depends on" in content_lower:
                relations.append({"type": "depends_on", "target": "unknown"})
            elif "instead" in content_lower or "switch" in content_lower:
                relations.append({"type": "contradicts", "target": "previous_goal"})

        rationale = f"[{state.activation_mode.name}] Confidence: {confidence:.2f}. "
        if should_propose:
            rationale += "Signals suggest a decision."
        else:
            rationale += "Insufficient signal strength."
            if relations and relations[0]["type"] == "contradicts":
                rationale += " (Contradiction detected)."

        return ProcessResult(
            confidence=confidence,
            should_propose=should_propose,
            rationale=rationale,
            signals=[{"name": s.name, "val": s.value} for s in signals],
            detected_relations=relations,
            activation_used=state.activation_mode.name
        )

    def contemplate_deep(self, current_confidence: float, content: str, memory_system: Any, relations: List) -> float:
        """
        The Reasoning Loop (Input + Memory + Logic -> Output).

        LOGIC:
        1. Extract Entities from `content`. (e.g., "Crypto").
        2. Query Context Web for those entities.
        3. Simulate Counter-Factuals: "If I delete Crypto, what happens to Project Chaos?"
        4. Check Long-Term Alignment: "Does this violate the 'Safety' constraint?"

        Returns:
            Adjusted Confidence Score.
        """
        # Basic heuristic implementation for now
        content_lower = content.lower()

        if "delete" in content_lower and "project" in content_lower:
             # LOGIC: Contradiction found in memory graph
             relations.append({"type": "contradicts", "target": "memory_constraint"})
             return current_confidence * 0.4 # Strong penalty

        # LOGIC: If checking "risk", query memory for risk tolerance
        if "risk" in content_lower:
             # Assume memory query returned "High Risk Tolerance"
             # return current_confidence * 1.2 # Boost
             pass

        return current_confidence

# Singleton
neural_hub = NeuralHub()
