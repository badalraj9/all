import unittest
from JARVIS.core.hardware.profile import detect_hardware, HardwareProfile

class TestHardwareProfile(unittest.TestCase):
    def test_detection(self):
        profile = detect_hardware()
        self.assertIsInstance(profile, HardwareProfile)
        self.assertGreater(profile.overall_score, 0)
        self.assertIsInstance(profile.compute_units, list)
        self.assertGreater(len(profile.compute_units), 0)
