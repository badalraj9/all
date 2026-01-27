from typing import Dict, Any, Tuple
from loguru import logger

from JARVIS.core.ule.types import ConversationState, MoveType
from JARVIS.core.ule.cognitive import AnchorExtractor, HypothesisGenerator
from JARVIS.core.ule.control import MoveSelector
from JARVIS.core.ule.dynamics import state_dynamics
from JARVIS.core.ule.realizer import realizer

class ULEEngine:
    """The Main ULE Loop: f(S, U) -> R"""

    def __init__(self):
        self.state = ConversationState()
        self.anchor_extractor = AnchorExtractor()
        self.hypothesis_generator = HypothesisGenerator()
        self.move_selector = MoveSelector()

    def process_turn(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        logger.info(f"ULE: Processing turn '{user_input}'")

        # 1. Cognitive Plane: Observation
        anchors = self.anchor_extractor.extract(user_input)
        hypotheses = self.hypothesis_generator.generate(anchors, self.state)

        # 2. Control Plane: Decision
        ule_output = self.move_selector.select_move(hypotheses, self.state)

        # 3. Execution & State Update
        action_payload = {}

        if ule_output.move == MoveType.CLARIFY:
            self.state.unresolved_gaps.append("ambiguity_resolution")

        elif ule_output.move == MoveType.PROPOSE:
            selected = ule_output.selected_interpretation
            self.state.topic = selected.intent
            action_payload = {
                "intent": selected.intent,
                "goal": selected.description
            }
            state_dynamics.update_trust(self.state, 1.0)

        # 4. REALIZATION (NLG) - The Voice
        natural_response = realizer.realize(ule_output)

        return natural_response, {
            "move": ule_output.move.name,
            "rationale": ule_output.rationale,
            "state": self.state.to_dict(),
            "action_payload": action_payload
        }

ule_engine = ULEEngine()
