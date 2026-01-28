from typing import Dict, Any, Tuple
from loguru import logger

from JARVIS.core.ule.types import ConversationState, MoveType
from JARVIS.core.ule.cognitive import AnchorExtractor, HypothesisGenerator
from JARVIS.core.ule.control import MoveSelector
from JARVIS.core.ule.dynamics import state_dynamics
from JARVIS.core.ule.realizer import realizer

class ULEEngine:
    def __init__(self):
        self.state = ConversationState()
        self.anchor_extractor = AnchorExtractor()
        self.hypothesis_generator = HypothesisGenerator()
        self.move_selector = MoveSelector()

    def process_turn(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        logger.info(f"ULE: Processing turn '{user_input}'")

        # 1. Cognitive Plane
        anchors = self.anchor_extractor.extract(user_input)

        # SPECIAL LOGIC: "Continue" / "Resume"
        # If input is just "continue", we bypass standard hypothesis generation
        # and look at the State Stack.
        if "continue" in user_input.lower() or "resume" in user_input.lower():
            if self.state.active_goal:
                # Resume current goal
                final_response = f"Resuming: {self.state.active_goal}"
                return final_response, {"move": "RESUME", "rationale": "Resuming active goal", "state": self.state.to_dict()}
            elif self.state.goal_stack:
                # Pop from stack
                self.state.active_goal = self.state.goal_stack.pop()
                final_response = f"Resuming previous task: {self.state.active_goal}"
                return final_response, {"move": "RESUME", "rationale": "Popped goal from stack", "state": self.state.to_dict()}
            else:
                return "I have no active tasks to resume.", {"move": "IDLE", "rationale": "Stack empty", "state": self.state.to_dict()}

        hypotheses = self.hypothesis_generator.generate(anchors, self.state)

        # 2. Control Plane
        ule_output = self.move_selector.select_move(hypotheses, self.state)

        # 3. State Update (Goal Tracking)
        action_payload = {}

        if ule_output.move == MoveType.PROPOSE:
            selected = ule_output.selected_interpretation
            # Update Goal State
            # Logic: If new goal is different from active, push active to stack
            if self.state.active_goal and self.state.active_goal != selected.description:
                self.state.push_goal(selected.description)
            else:
                self.state.active_goal = selected.description

            self.state.topic = selected.intent
            action_payload = {"intent": selected.intent, "goal": selected.description}
            state_dynamics.update_trust(self.state, 1.0)

        elif ule_output.move == MoveType.ANSWER:
            # Chit-chat does NOT change active goal
            pass

        # 4. Realization
        natural_response = realizer.realize(ule_output)

        return natural_response, {
            "move": ule_output.move.name,
            "rationale": ule_output.rationale,
            "state": self.state.to_dict(),
            "action_payload": action_payload
        }

ule_engine = ULEEngine()
