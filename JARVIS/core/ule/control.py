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
        # Formula: risk_adjusted = risk / (0.5 + trust)
        # trust=0.5 -> risk/1.0
        # trust=0.0 -> risk/0.5 (2x sensitivity)
        # trust=1.0 -> risk/1.5 (0.66x sensitivity)
        trust_factor = 1.0 / (0.5 + state.trust)

        return base_risk * trust_factor

class MoveSelector:
    """Implements Theorem 4.1: Optimal Move Selection."""

    def __init__(self):
        self.ambiguity_gauge = AmbiguityGauge()
        self.risk_assessor = RiskAssessor()
        self.A_crit = 0.6 # Critical Ambiguity Threshold
        self.Risk_Threshold = 0.7 # Safety Threshold

    def select_move(self, hypotheses: List[Interpretation], state: ConversationState) -> ULEOutput:
        # 1. Compute Ambiguity (Entropy)
        entropy = self.ambiguity_gauge.compute_entropy(hypotheses)

        # Theorem 2.3: Ambiguity-Risk Coupling
        if entropy > self.A_crit:
            return ULEOutput(
                move=MoveType.CLARIFY,
                rationale=f"Ambiguity {entropy:.2f} > {self.A_crit}. Clarification required.",
                selected_interpretation=None,
                response_content=self._generate_clarification(hypotheses)
            )

        best_h = max(hypotheses, key=lambda h: h.plausibility)

        # 2. Compute Risk
        risk = self.risk_assessor.evaluate_risk(best_h, state)

        # Theorem 4.2: Safety Guarantee
        if risk > self.Risk_Threshold:
            return ULEOutput(
                move=MoveType.REFUSE,
                rationale=f"Risk {risk:.2f} > {self.Risk_Threshold}.",
                selected_interpretation=None,
                response_content="Safety protocols prevent that action."
            )

        # 3. Safe -> PROPOSE
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
