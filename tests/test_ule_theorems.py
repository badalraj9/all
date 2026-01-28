import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from typing import List

from JARVIS.core.ule.types import ConversationState, Topic, Hypothesis, Move, MoveType, Risk, Anchors
from JARVIS.core.ule.cognitive import CognitivePlane
from JARVIS.core.ule.control import ConversationController
from JARVIS.core.ule.dynamics import Dynamics

class TestULETheorems(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.state = ConversationState(
            topic=Topic(name="Test"),
            trust=0.5,
            explicitness=0.5
        )
        self.cognitive = CognitivePlane(max_hypotheses=4)
        self.controller = ConversationController()
        self.dynamics = Dynamics()

    async def test_theorem_2_2_bounded_interpretation(self):
        """
        Theorem 2.2: |Hypotheses| <= k (k=4)
        """
        # Mock LLM to return many hypotheses text
        with patch('JARVIS.core.ule.cognitive.llm_engine') as mock_llm:
            mock_llm.generate = AsyncMock(return_value="raw output text")
            # Simulate a raw output that might imply many things,
            # but our parser (mocked or real) should handle it.
            # Here we rely on CognitivePlane logic which trims the list.

            # Since _parse_hypotheses is internal, we can check the result of generate_hypotheses
            # We'll mock _parse_hypotheses to return 10 items
            with patch.object(self.cognitive, '_parse_hypotheses') as mock_parse:
                mock_parse.return_value = [
                    Hypothesis(id=str(i), content=f"H{i}", confidence=0.1, reasoning="")
                    for i in range(10)
                ]

                anchors = Anchors(entities=[], intent_keywords=[], temporal_markers=[], raw_text="input")
                hypotheses = await self.cognitive.generate_hypotheses("input", self.state, anchors)

                # Assert
                self.assertLessEqual(len(hypotheses), 4)
                self.assertEqual(len(hypotheses), 4)
                print("\n[Passed] Theorem 2.2: Hypotheses bounded to 4.")

    def test_theorem_2_3_ambiguity_risk_coupling(self):
        """
        Theorem 2.3: High Ambiguity -> CLARIFY
        """
        # Case 1: High Entropy (Two hypotheses with 0.5 confidence)
        h1 = Hypothesis(id="1", content="Run generic", confidence=0.5, reasoning="")
        h2 = Hypothesis(id="2", content="Run specific", confidence=0.5, reasoning="")

        move = self.controller.select_move(self.state, [h1, h2])

        # Entropy of [0.5, 0.5] is -2 * (0.5 * ln(0.5)) approx 0.69
        # My controller threshold might be different. Let's check code constants.
        # AMBIGUITY_CRIT = 1.0.
        # Wait, ln(0.5) is -0.69. -0.5*-0.69 = 0.34. Sum = 0.69.
        # If I want > 1.0, I need more hypotheses.
        # 3 hypotheses: 0.33 each. ln(0.33)=-1.09. 0.33*1.09 = 0.36. Sum = 1.09.

        h3 = Hypothesis(id="3", content="Do nothing", confidence=0.5, reasoning="")

        move = self.controller.select_move(self.state, [h1, h2, h3]) # Normalized inside

        # Assert Clarification
        # Depending on logic, if entropy > 1.0 -> CLARIFY
        # 3 equal prob hypotheses have entropy > 1.09 (approx)
        self.assertEqual(move.type, MoveType.CLARIFY)
        print("\n[Passed] Theorem 2.3: High ambiguity forces CLARIFY.")

    def test_theorem_2_4_monotonic_trust(self):
        """
        Theorem 2.4: Trust updates are bounded.
        """
        # Huge signal
        feedback_signal = 100.0 # Should be clamped

        new_state = self.dynamics.update(self.state, "user", Move(type=MoveType.ANSWER, content="", rationale=""), feedback_signal)

        delta = new_state.trust - self.state.trust
        # Max beta is 0.1
        self.assertLessEqual(abs(delta), 0.1000001)
        print("\n[Passed] Theorem 2.4: Trust update bounded.")

    def test_theorem_2_5_explicitness_confidence(self):
        """
        Theorem 2.5: Low confidence/Clarification -> High Explicitness req
        """
        # If previous move was CLARIFY
        move = Move(type=MoveType.CLARIFY, content="?", rationale="")

        # Initial explicitness 0.5
        # Req for CLARIFY is 0.8
        # Gamma 0.3
        # New = 0.5 + 0.3 * (0.8 - 0.5) = 0.5 + 0.09 = 0.59

        new_state = self.dynamics.update(self.state, "user", move)
        self.assertGreater(new_state.explicitness, self.state.explicitness)
        print("\n[Passed] Theorem 2.5: Explicitness increased after Clarification.")

if __name__ == '__main__':
    unittest.main()
