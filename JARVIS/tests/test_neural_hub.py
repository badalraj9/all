import unittest
from JARVIS.intelligence.neural_hub.core import NeuralHub, ProcessingContext, NeuralState

class TestNeuralHub(unittest.TestCase):
    def test_decision_detection(self):
        hub = NeuralHub()
        state = NeuralState(user_id="u1", project_id="p1")
        ctx = ProcessingContext()

        # Test positive case
        result = hub.process("I have decided to go with plan A", ctx, state)
        self.assertTrue(result.should_propose)
        self.assertGreater(result.confidence, 0.5)

        # Test negative case
        result = hub.process("I am thinking about it", ctx, state)
        self.assertFalse(result.should_propose)
