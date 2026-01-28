from typing import Tuple
from JARVIS.core.ule.types import ConversationState, Move, Topic, Posture
from datetime import datetime

# CONSTANTS for Dynamics (Theorem 3.1 - 3.3)
ALPHA_TOPIC = 0.2  # Topic shift inertia
LAMBDA_TRUST = 0.9  # Trust decay/memory factor
TAU_BASELINE = 0.5  # Baseline trust
BETA_TRUST = 0.1    # Max trust update (delta_max)
GAMMA_EXPL = 0.3    # Explicitness control gain

class Dynamics:
    """
    Implements the State Transition Function f(S, U, R)
    """

    def update(self,
               state: ConversationState,
               user_utterance: str,
               system_response: Move,
               feedback_signal: float = 0.0) -> ConversationState:

        # Create new state (copy)
        new_state = state.model_copy()
        new_state.turn_count += 1
        new_state.last_updated = datetime.now()

        # 1. Update Topic (Theorem 3.1)
        # T_{t+1} = (1-alpha)T + alpha * shift(U)
        # Implementation: We treat the "name" as the primary manifold for now.
        # In full vector implementation, we would update embeddings.
        # Here we just mark it. The actual semantic shift happens via Cognitive Plane analysis.

        # 2. Update Trust (Theorem 3.2 & 2.4)
        # tau_{t+1} = lambda * tau + (1-lambda) * tau_base + beta * signal
        # Signal comes from explicit user feedback or sentiment analysis of U_{t+1} (here U is current)
        # Note: In the formal definition, trust updates based on U_{t+1} responding to R_t.
        # Here we apply the update for the *current* turn based on the *previous* interaction's result
        # embedded in the current utterance's sentiment/feedback.

        # Bounded update check
        delta_trust = (LAMBDA_TRUST * state.trust +
                       (1 - LAMBDA_TRUST) * TAU_BASELINE +
                       BETA_TRUST * feedback_signal) - state.trust

        # Clamp delta to [-BETA_TRUST, BETA_TRUST] (Theorem 2.4)
        delta_trust = max(-BETA_TRUST, min(BETA_TRUST, delta_trust))

        new_state.trust = max(0.0, min(1.0, state.trust + delta_trust))

        # 3. Update Explicitness (Theorem 3.3 & 2.5)
        # epsilon_{t+1} = epsilon + gamma * (req - epsilon)
        # Required explicitness is inversely proportional to system confidence in the *last* response.
        # If we just answered confidently, we can lower explicitness.
        # If we clarified, we increase it.

        req_explicitness = self._calculate_required_explicitness(system_response)
        new_state.explicitness = state.explicitness + GAMMA_EXPL * (req_explicitness - state.explicitness)

        # 4. Update Posture
        # Simple heuristic for now: Low trust -> Apologetic/Neutral
        if new_state.trust < 0.4:
            new_state.posture = Posture.APOLOGETIC
        elif new_state.trust > 0.8:
            new_state.posture = Posture.ENTHUSIASTIC
        else:
            new_state.posture = Posture.NEUTRAL

        return new_state

    def _calculate_required_explicitness(self, last_move: Move) -> float:
        # Theorem 2.5: Low confidence -> High explicitness
        # We approximate confidence based on Move Type
        if last_move.type in ["CLARIFY", "REFUSE"]:
            return 0.8  # High explicitness needed
        elif last_move.type == "ANSWER":
            return 0.2  # Can be concise
        elif last_move.type == "EXPLAIN":
            return 0.9  # Maximum explicitness
        return 0.5

dynamics = Dynamics()
