from typing import List, Dict, Optional, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime

from JARVIS.intelligence.math_utils import sigmoid, beta_variance, beta_mean
from JARVIS.intelligence.text_utils import tokenize, jaccard_similarity
from JARVIS.intelligence.constants import (
    DECISION_PATTERNS, QUICK_DECISION_PATTERN, STRUCTURAL_WEIGHTS,
    CHAT_TYPE_WEIGHTS, INTENT_ALIGNMENT_MAX, DEFAULT_THRESHOLD
)

# =============================================================================
# TYPES
# =============================================================================

@dataclass
class Signal:
    name: str
    type: Literal['linguistic', 'structural', 'contextual', 'temporal']
    value: float
    base_weight: float = 1.0

@dataclass
class NeuralState:
    user_id: str
    project_id: str
    weights: Dict[str, float] = field(default_factory=dict)
    threshold: float = DEFAULT_THRESHOLD
    alpha: float = 1.0  # Prior: 1 confirmation
    beta: float = 1.0   # Prior: 1 rejection
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProcessingContext:
    chat_type: str  # workshop, group_collab, etc.
    is_author_maintainer: bool
    participant_count: int
    thread_depth: int
    reaction_count: int
    reply_count: int
    recent_msg_rate: float
    avg_msg_rate: float
    active_intent: Optional[str]  # The intent statement
    message_timestamp: datetime
    discussion_start_time: Optional[datetime]

@dataclass
class SignalExplanation:
    name: str
    type: str
    raw_value: float
    weight: float
    contribution: float
    explanation: str

@dataclass
class ReasoningTrace:
    message_snippet: str
    chat_type: str
    has_active_intent: bool
    signals: List[SignalExplanation]
    aggregated_score: float
    threshold_used: float
    confidence_before_uncertainty: float
    uncertainty_factor: float
    final_confidence: float
    decision: Literal['propose', 'silence']
    decision_rationale: str

@dataclass
class EnhancedProcessResult:
    confidence: float
    should_propose: bool
    contributing_signals: List[Signal]
    aggregated_score: float
    reasoning: ReasoningTrace
    uncertainty_level: Literal['low', 'medium', 'high']

# =============================================================================
# SENSORS
# =============================================================================

class LinguisticSensor:
    def extract(self, content: str) -> List[Signal]:
        signals: List[Signal] = []
        for p in DECISION_PATTERNS:
            if p.compiled.search(content):
                signals.append(Signal(
                    name=p.name,
                    type='linguistic',
                    value=1.0,
                    base_weight=p.base_weight
                ))
        return signals

    def has_decision_markers(self, content: str) -> bool:
        return bool(QUICK_DECISION_PATTERN.search(content))

    def explain(self, signal_name: str) -> str:
        explanations = {
            'decided': 'Contains explicit decision language ("decided")',
            'lets_go_with': 'Contains commitment phrase ("let\'s go with")',
            'will_use': 'Contains future commitment ("we\'ll use")',
            'final': 'Contains closure signal ("final/finalized")',
            'settled_on': 'Contains resolution phrase ("settled on")',
            'going_with': 'Contains selection phrase ("going with/forward")',
            'agreed': 'Contains consensus marker ("agreed")',
            'pick': 'Contains selection verb ("pick/picked")',
            'choose': 'Contains selection verb ("choose/chose")',
        }
        return explanations.get(signal_name, f"Matched pattern: {signal_name}")

class StructuralSensor:
    def extract(self, ctx: ProcessingContext) -> List[Signal]:
        signals: List[Signal] = []

        # Thread depth
        depth_value = min(
            ctx.thread_depth * STRUCTURAL_WEIGHTS["thread_depth"]["multiplier"],
            STRUCTURAL_WEIGHTS["thread_depth"]["max"]
        )
        signals.append(Signal(name='thread_depth', type='structural', value=depth_value))

        # Maintainer authority
        if ctx.is_author_maintainer:
            signals.append(Signal(
                name='maintainer_author',
                type='structural',
                value=STRUCTURAL_WEIGHTS["maintainer_author"]["bonus"]
            ))

        # Acknowledgment ratio
        ack_ratio = (ctx.reaction_count + ctx.reply_count) / max(1, ctx.participant_count)
        ack_value = min(
            ack_ratio * STRUCTURAL_WEIGHTS["acknowledgment_ratio"]["multiplier"],
            STRUCTURAL_WEIGHTS["acknowledgment_ratio"]["max"]
        )
        signals.append(Signal(name='acknowledgment_ratio', type='structural', value=ack_value))

        # Debate burst
        if ctx.avg_msg_rate > 0:
            burst_factor = ctx.recent_msg_rate / ctx.avg_msg_rate
            burst_value = min(
                burst_factor / STRUCTURAL_WEIGHTS["debate_burst"]["divisor"],
                STRUCTURAL_WEIGHTS["debate_burst"]["max"]
            )
            signals.append(Signal(name='debate_burst', type='structural', value=burst_value))

        return signals

    def explain(self, signal_name: str, value: float) -> str:
        if signal_name == 'thread_depth':
            return f"Thread has {round(value / 0.03)} levels of replies"
        if signal_name == 'maintainer_author':
            return 'Message author is a project maintainer'
        if signal_name == 'acknowledgment_ratio':
            return f"{round(value * 20)}% acknowledgment from participants"
        if signal_name == 'debate_burst':
            return f"Activity is {round(value * 3 * 100)}% higher than average"
        return f"Structural signal: {signal_name}"

class ContextualSensor:
    def extract(self, content: str, ctx: ProcessingContext) -> List[Signal]:
        signals: List[Signal] = []

        # Chat type
        chat_type_weight = CHAT_TYPE_WEIGHTS.get(ctx.chat_type, 0.05)
        signals.append(Signal(name='chat_type', type='contextual', value=chat_type_weight))

        # Intent alignment
        if ctx.active_intent:
            similarity = self._compute_intent_alignment(content, ctx.active_intent)
            intent_value = similarity * INTENT_ALIGNMENT_MAX
            signals.append(Signal(name='intent_alignment', type='contextual', value=intent_value))

        return signals

    def _compute_intent_alignment(self, content: str, intent_statement: str) -> float:
        content_tokens = tokenize(content)
        intent_tokens = tokenize(intent_statement)
        return jaccard_similarity(content_tokens, intent_tokens)

    def explain(self, signal_name: str, value: float, ctx: ProcessingContext) -> str:
        if signal_name == 'chat_type':
            return f"Chat type: {ctx.chat_type}"
        if signal_name == 'intent_alignment':
            pct = round(value / INTENT_ALIGNMENT_MAX * 100)
            snippet = (ctx.active_intent[:50] + "...") if ctx.active_intent else "None"
            return f"{pct}% alignment with active intent: '{snippet}'"
        return f"Contextual signal: {signal_name}"

class TemporalSensor:
    def extract(self, ctx: ProcessingContext) -> List[Signal]:
        signals: List[Signal] = []
        now = ctx.message_timestamp
        hour = now.hour

        # Time of day
        time_weight = 0.0
        if 9 <= hour < 17:
            time_weight = 0.05
        elif 7 <= hour < 21:
            time_weight = 0.02

        if time_weight > 0:
            signals.append(Signal(name='working_hours', type='temporal', value=time_weight))

        # Discussion recency
        if ctx.discussion_start_time:
            duration_minutes = (now - ctx.discussion_start_time).total_seconds() / 60.0
            recency_weight = 0.0
            if 10 <= duration_minutes <= 60:
                recency_weight = 0.05
            elif 5 <= duration_minutes <= 120:
                recency_weight = 0.02

            if recency_weight > 0:
                signals.append(Signal(name='discussion_maturity', type='temporal', value=recency_weight))

        return signals

    def explain(self, signal_name: str, value: float) -> str:
        if signal_name == 'working_hours':
            return "Message sent during working hours"
        if signal_name == 'discussion_maturity':
            return "Discussion has reached decision-ready maturity"
        return f"Temporal signal: {signal_name}"

# =============================================================================
# SYNAPTIC PROCESSOR
# =============================================================================

class SynapticProcessor:
    def aggregate(self, signals: List[Signal], weights: Dict[str, float]) -> float:
        total = 0.0
        for signal in signals:
            weight = weights.get(signal.name, signal.base_weight)
            total += signal.value * weight
        return total

    def activate(self, aggregated: float, threshold: float, steepness: float = 10.0) -> float:
        return sigmoid(aggregated, threshold, steepness)

    def apply_uncertainty(self, confidence: float, state: NeuralState):
        variance = beta_variance(state.alpha, state.beta)
        uncertainty_factor = min(variance * 5, 0.3)
        adjusted = confidence * (1.0 - uncertainty_factor) + 0.5 * uncertainty_factor
        return adjusted, uncertainty_factor

# =============================================================================
# NEURAL HUB
# =============================================================================

class NeuralHub:
    def __init__(self):
        self.linguistic = LinguisticSensor()
        self.structural = StructuralSensor()
        self.contextual = ContextualSensor()
        self.temporal = TemporalSensor()
        self.processor = SynapticProcessor()

    def process(self, content: str, ctx: ProcessingContext, state: NeuralState) -> EnhancedProcessResult:
        # Tier 1: Quick linguistic check
        if not self.linguistic.has_decision_markers(content):
            return self._create_silent_result(content, ctx, "No decision language detected")

        # Tier 2: Signal extraction
        linguistic_signals = self.linguistic.extract(content)
        structural_signals = self.structural.extract(ctx)
        contextual_signals = self.contextual.extract(content, ctx)
        temporal_signals = self.temporal.extract(ctx)

        all_signals = linguistic_signals + structural_signals + contextual_signals + temporal_signals

        # Tier 3: Aggregation
        aggregated = self.processor.aggregate(all_signals, state.weights)

        # Tier 4: Activation
        effective_threshold = self._get_effective_threshold(state)
        raw_confidence = self.processor.activate(aggregated, effective_threshold)

        # Tier 5: Uncertainty
        final_confidence, uncertainty_factor = self.processor.apply_uncertainty(raw_confidence, state)

        # Tier 6: Decision
        should_propose = final_confidence >= 0.5

        # Tier 7: Reasoning Trace
        signal_explanations = self._build_explanations(all_signals, state, ctx)

        reasoning = ReasoningTrace(
            message_snippet=content[:100] + ("..." if len(content) > 100 else ""),
            chat_type=ctx.chat_type,
            has_active_intent=bool(ctx.active_intent),
            signals=signal_explanations,
            aggregated_score=aggregated,
            threshold_used=effective_threshold,
            confidence_before_uncertainty=raw_confidence,
            uncertainty_factor=uncertainty_factor,
            final_confidence=final_confidence,
            decision='propose' if should_propose else 'silence',
            decision_rationale=self._generate_rationale(should_propose, final_confidence, signal_explanations)
        )

        return EnhancedProcessResult(
            confidence=final_confidence,
            should_propose=should_propose,
            contributing_signals=all_signals,
            aggregated_score=aggregated,
            reasoning=reasoning,
            uncertainty_level=self._get_uncertainty_level(state)
        )

    def _get_effective_threshold(self, state: NeuralState) -> float:
        acceptance_rate = beta_mean(state.alpha, state.beta)
        adjustment = (0.5 - acceptance_rate) * 0.15
        return max(0.60, min(0.90, state.threshold + adjustment))

    def _build_explanations(self, signals: List[Signal], state: NeuralState, ctx: ProcessingContext) -> List[SignalExplanation]:
        explanations = []
        for s in signals:
            weight = state.weights.get(s.name, s.base_weight)
            contribution = s.value * weight

            explanation_text = ""
            if s.type == 'linguistic':
                explanation_text = self.linguistic.explain(s.name)
            elif s.type == 'structural':
                explanation_text = self.structural.explain(s.name, s.value)
            elif s.type == 'contextual':
                explanation_text = self.contextual.explain(s.name, s.value, ctx)
            elif s.type == 'temporal':
                explanation_text = self.temporal.explain(s.name, s.value)

            explanations.append(SignalExplanation(
                name=s.name,
                type=s.type,
                raw_value=s.value,
                weight=weight,
                contribution=contribution,
                explanation=explanation_text
            ))

        # Sort by contribution descending
        explanations.sort(key=lambda x: x.contribution, reverse=True)
        return explanations

    def _generate_rationale(self, should_propose: bool, confidence: float, signals: List[SignalExplanation]) -> str:
        top_signals = signals[:3]
        pct = round(confidence * 100)
        reasons = "; ".join([s.explanation for s in top_signals])

        if should_propose:
            return f"Proposing decision ({pct}% confidence). Key factors: {reasons}"
        else:
            if confidence > 0.3:
                return f"Not enough evidence ({pct}% confidence). Would need stronger signals."
            else:
                return f"Low decision likelihood ({pct}% confidence)."

    def _get_uncertainty_level(self, state: NeuralState) -> str:
        total_obs = state.alpha + state.beta - 2
        if total_obs < 5: return 'high'
        if total_obs < 20: return 'medium'
        return 'low'

    def _create_silent_result(self, content: str, ctx: ProcessingContext, reason: str) -> EnhancedProcessResult:
        # Empty reasoning trace for silent result
        reasoning = ReasoningTrace(
            message_snippet=content[:100],
            chat_type=ctx.chat_type,
            has_active_intent=bool(ctx.active_intent),
            signals=[],
            aggregated_score=0.0,
            threshold_used=DEFAULT_THRESHOLD,
            confidence_before_uncertainty=0.0,
            uncertainty_factor=0.0,
            final_confidence=0.0,
            decision='silence',
            decision_rationale=reason
        )
        return EnhancedProcessResult(
            confidence=0.0,
            should_propose=False,
            contributing_signals=[],
            aggregated_score=0.0,
            reasoning=reasoning,
            uncertainty_level='high'
        )

# Singleton
neural_hub = NeuralHub()
