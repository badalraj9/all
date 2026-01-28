from typing import List
from JARVIS.core.ule.types import Hypothesis, ConversationState, Anchors, Risk
from JARVIS.intelligence.llm_engine import llm_engine
import uuid
import json

class CognitivePlane:
    def __init__(self, max_hypotheses: int = 4):
        self.max_hypotheses = max_hypotheses  # Enforcing Theorem 2.2

    async def extract_anchors(self, utterance: str) -> Anchors:
        """
        Extracts semantic anchors from raw input.
        This is the 'Anchors: Input -> P(Semantic Primitives)' mapping.
        """
        # In a full implementation, this uses the LLM or a specialized NLP model.
        # For now, we simulate extraction or use a simple prompt.
        prompt = f"""
        Extract semantic anchors from the following utterance.
        Return strictly valid JSON with keys: entities, intent_keywords, temporal_markers.
        Utterance: "{utterance}"
        """
        response = await llm_engine.generate(prompt)

        # Mocking parsing for resilience
        # In real impl, we'd use a robust JSON parser
        return Anchors(
            entities=[],
            intent_keywords=["unknown"],
            temporal_markers=[],
            raw_text=utterance
        )

    async def generate_hypotheses(self, utterance: str, state: ConversationState, anchors: Anchors) -> List[Hypothesis]:
        """
        H = {h1, ..., hk} ~ p(hypothesis | anchors, state)
        Subject to |H| <= k (Theorem 2.2)
        """

        # Construct prompt for the LLM to generate multiple interpretations
        prompt = self._construct_hypothesis_prompt(utterance, state, anchors)

        # Get raw generation
        raw_output = await llm_engine.generate(prompt, max_tokens=500)

        # Parse into structured Hypotheses
        hypotheses = self._parse_hypotheses(raw_output)

        # Enforce Bounded Interpretation Principle
        return hypotheses[:self.max_hypotheses]

    def _construct_hypothesis_prompt(self, utterance: str, state: ConversationState, anchors: Anchors) -> str:
        return f"""
        Analyze the user utterance given the current conversation state.
        State Topic: {state.topic.name}
        User Utterance: "{utterance}"

        Generate up to {self.max_hypotheses} distinct interpretations (hypotheses) of what the user means.
        For each hypothesis, assign a confidence score (0.0 to 1.0) and a risk level.
        """

    def _parse_hypotheses(self, raw_output: str) -> List[Hypothesis]:
        # Placeholder parser. In reality, we'd force JSON output from LLM.
        # Returning a single dummy hypothesis if parsing fails to ensure system continuity.
        return [
            Hypothesis(
                id=str(uuid.uuid4()),
                content=raw_output[:100], # Trucated
                confidence=0.5,
                reasoning="Default hypothesis from raw output",
                risk_assessment=Risk(score=0.1, factors=[], is_safe=True)
            )
        ]

cognitive_plane = CognitivePlane()
