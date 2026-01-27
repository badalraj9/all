import math
from typing import List
from JARVIS.core.ule.types import Interpretation, ConversationState, MoveType, ULEOutput

class AmbiguityGauge:
    """Implements Theorem 2.3: Ambiguity Quantification (Entropy)."""

    def compute_entropy(self, hypotheses: List[Interpretation]) -> float:
        if not hypotheses:
            return 0.0

        total_p = sum(h.plausibility for h in hypotheses)
        if total_p == 0:
            return 0.0

        probs = [h.plausibility / total_p for h in hypotheses]
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        return entropy

class RiskAssessor:
    """Implements Risk Assessment based on Theorem 3.4."""

    def evaluate_risk(self, hypothesis: Interpretation, state: ConversationState) -> float:
        base_risk = hypothesis.risk_score

        # Risk sensitivity increases as trust decreases
        # trust=0.0 -> multiplier 2.0 (Conservative)
        # trust=1.0 -> multiplier 1.0 (Relaxed)
        trust_factor = 2.0 / (1.0 + state.trust)

        return base_risk * trust_factor

class MoveSelector:
    """Implements Theorem 4.1: Optimal Move Selection."""

    def __init__(self):
        self.ambiguity_gauge = AmbiguityGauge()
        self.risk_assessor = RiskAssessor()
        self.A_crit = 0.5
        self.Risk_Threshold = 0.6 # Stricter threshold

    def select_move(self, hypotheses: List[Interpretation], state: ConversationState) -> ULEOutput:
        entropy = self.ambiguity_gauge.compute_entropy(hypotheses)

        if entropy > self.A_crit:
            return ULEOutput(
                move=MoveType.CLARIFY,
                rationale=f"Ambiguity {entropy:.2f} > {self.A_crit}. Clarification required.",
                selected_interpretation=None,
                response_content=self._generate_clarification(hypotheses)
            )

        best_h = max(hypotheses, key=lambda h: h.plausibility)

        # If best hypothesis is weak (plausibility < 0.3), don't act
        if best_h.plausibility < 0.3:
             return ULEOutput(
                move=MoveType.CLARIFY,
                rationale=f"Best hypothesis weak ({best_h.plausibility:.2f}). Clarifying.",
                selected_interpretation=None,
                response_content="I'm not sure I understand."
            )

        risk = self.risk_assessor.evaluate_risk(best_h, state)

        if risk > self.Risk_Threshold:
            return ULEOutput(
                move=MoveType.REFUSE,
                rationale=f"Risk {risk:.2f} > {self.Risk_Threshold}.",
                selected_interpretation=None,
                response_content="Safety protocols prevent that action."
            )

        return ULEOutput(
            move=MoveType.PROPOSE,
            rationale=f"Ambiguity low ({entropy:.2f}), Risk acceptable ({risk:.2f}).",
            selected_interpretation=best_h,
            response_content=f"Proceeding with: {best_h.description}"
        )

    def _generate_clarification(self, hypotheses: List[Interpretation]) -> str:
        options = [f"'{h.entities[0] if h.entities else h.intent}'" for h in hypotheses]
        if len(options) >= 2:
            return f"Did you mean {options[0]} or {options[1]}?"
        return "Could you clarify?"
