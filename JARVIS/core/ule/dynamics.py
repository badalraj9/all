from JARVIS.core.ule.types import ConversationState, MoveType

class StateDynamics:
    """
    Implements Part III: State Transition Dynamics.
    """

    def __init__(self, delta_max: float = 0.1):
        self.delta_max = delta_max # Theorem 2.4: Bounded Updates

    def update_trust(self, state: ConversationState, signal: float) -> ConversationState:
        """
        Theorem 3.2: Trust Evolution.
        τ_{t+1} = λ·τ_t + β·signal
        """
        # Bounded update
        clamped_signal = max(-self.delta_max, min(self.delta_max, signal * 0.1))

        new_trust = max(0.0, min(1.0, state.trust + clamped_signal))
        state.trust = new_trust
        return state

    def update_explicitness(self, state: ConversationState, confidence: float) -> ConversationState:
        """
        Theorem 2.5: Explicitness-Confidence Duality.
        Low confidence -> High explicitness required.
        """
        # Inverse Law: ε ~ 1 - c
        target_epsilon = 1.0 - confidence

        # P-Controller (Theorem 3.3)
        gamma = 0.3
        state.explicitness += gamma * (target_epsilon - state.explicitness)

        return state

state_dynamics = StateDynamics()
