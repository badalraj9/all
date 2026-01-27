import math
from typing import List
from JARVIS.core.ule.types import Interpretation, ConversationState, MoveType, ULEOutput

class AmbiguityGauge:
    """Implements Theorem 2.3: Ambiguity Quantification (Entropy)."""

    def compute_entropy(self, hypotheses: List[Interpretation]) -> float:
        if not hypotheses:
            return 0.0

        # Normalize plausibility to probabilities
        total_p = sum(h.plausibility for h in hypotheses)
        if total_p == 0:
            return 0.0

        probs = [h.plausibility / total_p for h in hypotheses]

        # H(X) = -Sum(p * log(p))
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        return entropy

class RiskAssessor:
    """Implements Risk Assessment based on Theorem 3.4."""

    def evaluate_risk(self, hypothesis: Interpretation, state: ConversationState) -> float:
        # risk(h) = irreversibility * cost * trust_sensitivity
        # For V1, we simplify:

        base_risk = hypothesis.risk_score
        trust_factor = 1.0 / (1.0 + state.trust) # Low trust -> Higher risk

        return base_risk * trust_factor

class MoveSelector:
    """Implements Theorem 4.1: Optimal Move Selection."""

    def __init__(self):
        self.ambiguity_gauge = AmbiguityGauge()
        self.risk_assessor = RiskAssessor()
        self.A_crit = 0.5 # Critical Ambiguity Threshold

    def select_move(self, hypotheses: List[Interpretation], state: ConversationState) -> ULEOutput:
        # 1. Compute Ambiguity (Entropy)
        entropy = self.ambiguity_gauge.compute_entropy(hypotheses)

        # 2. Theorem 2.3: Ambiguity-Risk Coupling
        if entropy > self.A_crit:
            # High Ambiguity -> Must CLARIFY
            return ULEOutput(
                move=MoveType.CLARIFY,
                rationale=f"Ambiguity {entropy:.2f} > {self.A_crit}. Clarification required.",
                selected_interpretation=None,
                response_content=self._generate_clarification(hypotheses)
            )

        # 3. Low Ambiguity -> Check Risk of best hypothesis
        best_h = max(hypotheses, key=lambda h: h.plausibility)
        risk = self.risk_assessor.evaluate_risk(best_h, state)

        # Theorem 4.2: Safety Guarantee
        # If risk > threshold, REFUSE or EXPLAIN
        risk_threshold = 0.8 # Simplified constant for V1

        if risk > risk_threshold:
            return ULEOutput(
                move=MoveType.REFUSE,
                rationale=f"Risk {risk:.2f} too high for trust {state.trust:.2f}.",
                selected_interpretation=None,
                response_content="I cannot do that safely."
            )

        # 4. Safe -> PROPOSE/ANSWER
        return ULEOutput(
            move=MoveType.PROPOSE,
            rationale=f"Ambiguity low ({entropy:.2f}), Risk acceptable ({risk:.2f}).",
            selected_interpretation=best_h,
            response_content=f"Proceeding with: {best_h.description}"
        )

    def _generate_clarification(self, hypotheses: List[Interpretation]) -> str:
        options = [f"'{h.entities[0] if h.entities else h.intent}'" for h in hypotheses]
        return f"Did you mean {options[0]} or {options[1]}?" if len(options) >= 2 else "Could you clarify?"
