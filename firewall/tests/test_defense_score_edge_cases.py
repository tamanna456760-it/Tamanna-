"""Edge-case tests for Tamanna AI firewall defense scoring."""
import unittest
from firewall.defense_score import CONTROL_WEIGHTS, calculate_defense_score
class TestDefenseScoreEdgeCases(unittest.TestCase):
    def test_control_weights_are_available(self):
        """Defense score should define its control weights."""
        self.assertIsInstance(CONTROL_WEIGHTS, dict)
        self.assertGreater(len(CONTROL_WEIGHTS), 0)
    def test_all_controls_disabled_produces_low_score(self):
        """Disabled controls should not produce a perfect readiness score."""
        controls = {name: False for name in CONTROL_WEIGHTS}
        result = calculate_defense_score(controls)
        if isinstance(result, dict):
            score = result.get("score", result.get("defense_score"))
        else:
            score = result
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertLess(score, 100)
    def test_all_controls_enabled_score_is_bounded(self):
        """The score should stay within the documented 0–100 range."""
        controls = {name: True for name in CONTROL_WEIGHTS}
        result = calculate_defense_score(controls)
        if isinstance(result, dict):
            score = result.get("score", result.get("defense_score"))
        else:
            score = result
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
if __name__ == "__main__":
    unittest.main()