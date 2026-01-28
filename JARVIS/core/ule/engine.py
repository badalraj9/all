from typing import Dict, Tuple, Any
from JARVIS.core.ule.types import ConversationState, Topic, Move, Anchors
from JARVIS.core.ule.cognitive import cognitive_plane
from JARVIS.core.ule.control import controller
from JARVIS.core.ule.dynamics import dynamics
from JARVIS.intelligence.llm_engine import llm_engine
from loguru import logger
import asyncio

class ULEEngine:
    def __init__(self):
        self.states: Dict[str, ConversationState] = {}

    async def initialize(self):
        # Initialize LLM
        await llm_engine.initialize()

    def get_or_create_state(self, user_id: str) -> ConversationState:
        if user_id not in self.states:
            self.states[user_id] = ConversationState(
                topic=Topic(name="General"),
                trust=0.5,
                explicitness=0.5
            )
        return self.states[user_id]

    async def process_turn(self, user_id: str, user_text: str) -> Tuple[str, Dict[str, Any]]:
        # 1. Get State (S_t)
        state = self.get_or_create_state(user_id)
        logger.info(f"ULE: Processing turn {state.turn_count} for user {user_id}. Trust={state.trust:.2f}")

        # 2. Cognitive Plane (V): Input -> Hypotheses
        anchors = await cognitive_plane.extract_anchors(user_text)
        hypotheses = await cognitive_plane.generate_hypotheses(user_text, state, anchors)
        logger.debug(f"ULE: Generated {len(hypotheses)} hypotheses.")

        # 3. Conversation Plane (C): State + Hypotheses -> Move
        move = controller.select_move(state, hypotheses)
        logger.info(f"ULE: Selected Move: {move.type} | Rationale: {move.rationale}")

        # 4. Realization (M -> Response Text)
        response_text = await self._realize_move(move, state)

        # 5. Dynamics (f): S_{t+1} = f(S_t, U_t, R_t)
        new_state = dynamics.update(state, user_text, move)
        self.states[user_id] = new_state

        # 6. Metadata for UI/Systems
        meta = {
            "state": {
                "trust": new_state.trust,
                "explicitness": new_state.explicitness,
                "ambiguity": controller._calculate_entropy(hypotheses) # Recalculating for display or pass it
            },
            "move": move.type,
            "rationale": move.rationale,
            # If the move was PROPOSE, we assume the content or metadata has the goal.
            # For now, we'll extract it heuristically or from hypothesis.
            "action_payload": move.metadata.get("action_payload")
        }

        return response_text, meta

    async def _realize_move(self, move: Move, state: ConversationState) -> str:
        prompt = f"""
        Generate a response for the user.
        Move Type: {move.type}
        Content Intent: {move.content}
        Target Explicitness: {state.explicitness} (0=concise, 1=very detailed)
        Posture: {state.posture.value}
        """
        response = await llm_engine.generate(prompt, max_tokens=200)
        return response

ule_engine = ULEEngine()
