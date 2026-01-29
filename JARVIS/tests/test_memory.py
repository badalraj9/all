import unittest
from JARVIS.memory.system import MemorySystem
from JARVIS.memory.core_models import MemoryEvent, MemoryType

class TestMemorySystem(unittest.TestCase):
    def test_log_event(self):
        # Mock postgres client
        class MockPG:
            def execute(self, query, params): pass

        system = MemorySystem(MockPG())
        event = system.log_event(
            actor="USER",
            action="TEST",
            object_id="test-obj-1",
            payload={"test": "data"},
            confidence=0.9
        )

        self.assertIsInstance(event, MemoryEvent)
        self.assertEqual(event.actor, "USER")
        self.assertEqual(event.truth_vector.confidence, 0.9)
