from typing import Dict, Any, Tuple
from loguru import logger

from JARVIS.core.ule.types import ConversationState, MoveType
from JARVIS.core.ule.cognitive import AnchorExtractor, HypothesisGenerator
from JARVIS.core.ule.control import MoveSelector
from JARVIS.core.ule.dynamics import state_dynamics

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
            # Update state to reflect ambiguity gap
            self.state.unresolved_gaps.append("ambiguity_resolution")
            # Response is the clarification question
            final_response = ule_output.response_content

        elif ule_output.move == MoveType.PROPOSE:
            # We have a solid intent -> Execute
            selected = ule_output.selected_interpretation
            self.state.topic = selected.intent

            # Map interpretation to Action Payload for MissionControl
            action_payload = {
                "intent": selected.intent,
                "goal": selected.description
            }

            final_response = f"Affirmative. {ule_output.response_content}"
            # Trust grows slightly on successful proposal
            state_dynamics.update_trust(self.state, 1.0)

        elif ule_output.move == MoveType.REFUSE:
            final_response = f"Safety Lock: {ule_output.response_content}"

        else:
            final_response = "Processing..."

        return final_response, {
            "move": ule_output.move.name,
            "rationale": ule_output.rationale,
            "state": self.state.to_dict(),
            "action_payload": action_payload
        }

ule_engine = ULEEngine()
