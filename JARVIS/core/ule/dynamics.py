from JARVIS.core.ule.types import ConversationState

class StateDynamics:
    """Implements Part III: State Transition Dynamics."""

    def __init__(self, delta_max: float = 0.1):
        self.delta_max = delta_max # Max trust increment (Theorem 2.4)

    def update_trust(self, state: ConversationState, signal: float) -> ConversationState:
        """
        Theorem 3.2: Trust Evolution.
        signal: +1 (success), -1 (failure)
        """
        # Bounded update
        clamped_signal = max(-self.delta_max, min(self.delta_max, signal * 0.05))

        new_trust = max(0.0, min(1.0, state.trust + clamped_signal))
        state.trust = new_trust
        return state

    def update_explicitness(self, state: ConversationState, confidence: float) -> ConversationState:
        """
        Theorem 2.5: Explicitness-Confidence Duality.
        Low confidence -> High explicitness required.
        """
        # Simple Inverse Law: epsilon ~ 1/confidence
        target_epsilon = 1.0 - confidence

        # P-Controller update (Theorem 3.3)
        gamma = 0.3 # Control gain
        state.explicitness += gamma * (target_epsilon - state.explicitness)

        return state

state_dynamics = StateDynamics()
