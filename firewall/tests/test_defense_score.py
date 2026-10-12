"""
Tamanna AI — Defense Score Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_defense_score -v
Tests use local data and temporary files only.
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.defense_score import (
    CONTROL_WEIGHTS,
    calculate_defense_score,
    save_defense_report,
)
class TestDefenseScoreCalculation(unittest.TestCase):
    def test_all_controls_passing_scores_100(self):
        checks = {
            name: True
            for name in CONTROL_WEIGHTS
        }
        result = calculate_defense_score(checks)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["maximum_score"], 100)
        self.assertEqual(
            result["passed_controls"],
            len(CONTROL_WEIGHTS),
        )
    def test_no_controls_passing_scores_zero(self):
        result = calculate_defense_score({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["passed_controls"], 0)
    def test_single_control_awards_its_weight(self):
        checks = {"policy_validation": True}
        result = calculate_defense_score(checks)
        self.assertEqual(
            result["score"],
            CONTROL_WEIGHTS["policy_validation"],
        )
        self.assertEqual(result["passed_controls"], 1)
    def test_false_control_does_not_earn_points(self):
        checks = {"authentication": False}
        result = calculate_defense_score(checks)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["passed_controls"], 0)
    def test_missing_controls_are_reported(self):
        result = calculate_defense_score({})
        self.assertEqual(
            set(result["missing_controls"]),
            set(CONTROL_WEIGHTS),
        )
    def test_unknown_controls_are_not_counted(self):
        result = calculate_defense_score({
            "unknown_control": True,
        })
        self.assertEqual(result["score"], 0)
        self.assertIn(
            "unknown_control",
            result["unknown_controls"],
        )
    def test_truthy_non_boolean_does_not_pass(self):
        result = calculate_defense_score({
            "authentication": "yes",
        })
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["passed_controls"], 0)
    def test_invalid_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_defense_score(["authentication"])
class TestDefenseScoreLevels(unittest.TestCase):
    def test_score_level_is_returned(self):
        result = calculate_defense_score({})
        self.assertIn(
            result["level"],
            {"strong", "good", "needs_improvement", "weak"},
        )
    def test_score_never_exceeds_100(self):
        result = calculate_defense_score({
            name: True for name in CONTROL_WEIGHTS
        })
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
    def test_limitations_are_disclosed(self):
        result = calculate_defense_score({})
        self.assertTrue(result["limitations"])
        self.assertTrue(
            any("not" in item.lower()
                for item in result["limitations"])
        )
class TestDefenseReport(unittest.TestCase):
    def test_report_is_saved_as_json(self):
        report = calculate_defense_score({
            "policy_validation": True,
        })
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "defense_score.json"
            saved_path = save_defense_report(report, output)
            self.assertTrue(saved_path.exists())
            payload = json.loads(
                saved_path.read_text(encoding="utf-8")
            )
            self.assertIn("generated_at", payload)
            self.assertIn("report", payload)
            self.assertEqual(
                payload["report"]["score"],
                report["score"],
            )
    def test_report_parent_directory_is_created(self):
        report = calculate_defense_score({})
        with tempfile.TemporaryDirectory() as temp_dir:
            output = (
                Path(temp_dir)
                / "reports"
                / "nested"
                / "defense_score.json"
            )
            saved_path = save_defense_report(report, output)
            self.assertTrue(saved_path.exists())
if __name__ == "__main__":
    unittest.main(verbosity=2)