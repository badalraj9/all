import math
from typing import List, Optional
from JARVIS.core.ule.types import ConversationState, Hypothesis, Move, MoveType, Risk
from loguru import logger

# Constants
AMBIGUITY_CRIT = 1.0  # Critical entropy threshold (approx 2 equally likely hypotheses)
RISK_ALPHA = 0.4      # Base risk constant

class ConversationController:
    """
    Implements the Conversation Control Function C(S, H) -> M
    """

    def select_move(self, state: ConversationState, hypotheses: List[Hypothesis]) -> Move:
        # 1. Calculate Ambiguity (Entropy) - Theorem 2.3
        ambiguity = self._calculate_entropy(hypotheses)
        logger.info(f"ULE: Hypotheses Entropy = {ambiguity:.3f} (Critical: {AMBIGUITY_CRIT})")

        # 2. Calculate Risk Threshold (Theorem 2.3 / 4.1)
        # Threshold decreases as trust decreases
        risk_threshold = RISK_ALPHA / (1.0 + state.trust)
        logger.info(f"ULE: Risk Threshold = {risk_threshold:.3f} (Trust: {state.trust:.2f})")

        # 3. Evaluate Moves (Theorem 4.1)
        possible_moves = []

        # Scenario A: High Ambiguity -> Force CLARIFY or REFUSE (Theorem 2.3)
        if ambiguity > AMBIGUITY_CRIT:
            logger.warning("ULE: High ambiguity detected. Forcing clarification.")
            return self._create_clarification_move(hypotheses, state)

        # Scenario B: Optimization
        # Find best hypothesis
        if not hypotheses:
             return Move(type=MoveType.REFUSE, content="I'm not sure I understand.", rationale="No hypotheses generated.")

        best_h = max(hypotheses, key=lambda h: h.confidence)

        # Assess risk of acting on best_h
        h_risk = self._assess_risk(best_h, state)

        if h_risk > risk_threshold:
            logger.warning(f"ULE: Action risk ({h_risk:.2f}) exceeds threshold. Refusing/Clarifying.")
            return self._create_clarification_move(hypotheses, state)

        # If safe, choose ANSWER or PROPOSE based on content
        return self._create_answer_move(best_h, state)

    def _calculate_entropy(self, hypotheses: List[Hypothesis]) -> float:
        if not hypotheses: return 0.0
        # Normalize confidences
        total_conf = sum(h.confidence for h in hypotheses)
        if total_conf == 0: return 0.0

        probs = [h.confidence / total_conf for h in hypotheses]
        entropy = -sum(p * math.log(p + 1e-9) for p in probs) # natural log
        return entropy

    def _assess_risk(self, hypothesis: Hypothesis, state: ConversationState) -> float:
        # Simplified risk function:
        # risk = (1 - confidence) * impact
        # Assume generic impact for now. In real system, check if action is reversible.
        impact = 0.8 # Assume high impact for conversational errors
        if hypothesis.risk_assessment:
            impact = hypothesis.risk_assessment.score

        return (1.0 - hypothesis.confidence) * impact

    def _create_clarification_move(self, hypotheses: List[Hypothesis], state: ConversationState) -> Move:
        # Generate clarification content
        # E.g., "Do you mean X or Y?"
        options = [h.content for h in hypotheses[:2]] # Top 2 options
        content = f"Could you clarify? Do you mean {options[0]} or {options[1]}?" if len(options) > 1 else "Could you clarify what you mean?"

        return Move(
            type=MoveType.CLARIFY,
            content=content,
            rationale="Ambiguity/Risk too high for direct answer."
        )

    def _create_answer_move(self, hypothesis: Hypothesis, state: ConversationState) -> Move:
        # Generate answer based on hypothesis
        # In full system, this would call a Generator/Realizer component.
        return Move(
            type=MoveType.ANSWER,
            content=f"[Answering: {hypothesis.content}]", # Placeholder for realization
            rationale=f"Confidence {hypothesis.confidence} sufficient.",
            target_hypothesis_id=hypothesis.id
        )

controller = ConversationController()
