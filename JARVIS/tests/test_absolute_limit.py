import unittest
import os
import networkx as nx
from PIL import Image
from JARVIS.memory.system import MemorySystem
from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext
from JARVIS.plugins.vision_marey.plugin import VisionPlugin

class TestAbsoluteLimit(unittest.TestCase):

    def test_vision_pipeline(self):
        """
        Verify Real Saliency Detection (Low-Res Scan).
        """
        print("\n--- TEST: VISION LIMIT ---")
        # Create dummy image: White background, Black square in Top-Right
        img = Image.new('RGB', (1000, 1000), color='white')
        pixels = img.load()
        for i in range(500, 1000):
            for j in range(0, 500):
                pixels[i, j] = (0, 0, 0) # Top-Right Quadrant is "busy"

        img_path = "test_vision.png"
        img.save(img_path)

        plugin = VisionPlugin()
        result = plugin.analyze_image(img_path)
        print(f"Vision Output: {result}")

        # Expected: High Variance detected
        self.assertIn("Analyzed Crop", result)

        os.remove(img_path)

    def test_memory_graph_dynamics(self):
        """
        Verify Real Graph Traversal (Spread Activation).
        """
        print("\n--- TEST: MEMORY LIMIT ---")
        memory = MemorySystem()

        # Build Graph: Start -> Middle -> End
        memory.add_relation("Start", "Middle", "depends_on", weight=1.0)
        memory.add_relation("Middle", "End", "depends_on", weight=1.0)

        # Traverse
        activation = memory.spread_activation("Start", initial_energy=1.0, decay=0.9)
        print(f"Activation Map: {activation}")

        self.assertIn("Middle", activation)
        self.assertIn("End", activation)
        self.assertGreater(activation["Start"], activation["Middle"])
        self.assertGreater(activation["Middle"], activation["End"])

    def test_reasoning_loop(self):
        """
        Verify Deep Contemplation (Contradiction Check).
        """
        print("\n--- TEST: REASONING LIMIT ---")
        memory = MemorySystem()
        neural = NeuralHub()
        state = NeuralState(user_id="test", project_id="limit")
        ctx = ProcessingContext()

        # Setup: Project Alpha depends on Crypto
        memory.add_relation("Project Alpha", "Crypto", "depends_on", weight=1.0)

        # Action: "Delete Crypto"
        msg = "Delete Crypto now."
        print(f"User: {msg}")

        res = neural.process(msg, ctx, state, memory_system=memory)
        print(f"Result: {res.rationale}")

        # Expected: Contradiction found -> Confidence penalized
        self.assertIn("Contradiction detected", res.rationale)
        self.assertFalse(res.should_propose) # Should be blocked

if __name__ == "__main__":
    unittest.main()
