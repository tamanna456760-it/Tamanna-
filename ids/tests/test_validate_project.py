"""Tests for Tamanna AI IDS project validation."""
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from ids import validate_project
VALID_CONFIG = {
    "project": "Tamanna AI",
    "mode": "monitor_only",
    "enforcement": {
        "automatic_ip_blocking": False,
        "modify_system_firewall": False,
        "manual_approval": True,
    },
}
HEALTHY_RESULT = {
    "status": "healthy",
    "system_firewall_modified": False,
}
class TestValidateProject(unittest.TestCase):
    """Test project validation without touching system settings."""
    def run_validation(self):
        output = StringIO()
        with redirect_stdout(output):
            result = validate_project.main()
        return result, output.getvalue()
    @patch("ids.validate_project.run_health_check", return_value=HEALTHY_RESULT)
    @patch("ids.validate_project.IDSManager")
    @patch("ids.validate_project.load_config", return_value=VALID_CONFIG)
    def test_valid_project_passes(
        self, mock_load, mock_manager, mock_health
    ):
        result, output = self.run_validation()
        self.assertEqual(result, 0)
        self.assertIn("[PASS] Configuration loaded", output)
        self.assertIn("[PASS] Project validation completed", output)
        mock_manager.assert_called_once_with(mode="monitor_only")
        mock_health.assert_called_once()
    @patch(
        "ids.validate_project.load_config",
        return_value={**VALID_CONFIG, "mode": "active"},
    )
    def test_non_monitor_mode_fails(self, mock_load):
        result, output = self.run_validation()
        self.assertEqual(result, 1)
        self.assertIn("monitor_only mode", output)
    @patch(
        "ids.validate_project.load_config",
        return_value={
            **VALID_CONFIG,
            "enforcement": {
                **VALID_CONFIG["enforcement"],
                "automatic_ip_blocking": True,
            },
        },
    )
    def test_automatic_blocking_fails(self, mock_load):
        result, output = self.run_validation()
        self.assertEqual(result, 1)
        self.assertIn("Automatic IP blocking must be disabled", output)
    @patch(
        "ids.validate_project.load_config",
        return_value={
            **VALID_CONFIG,
            "enforcement": {
                **VALID_CONFIG["enforcement"],
                "modify_system_firewall": True,
            },
        },
    )
    def test_firewall_modification_fails(self, mock_load):
        result, output = self.run_validation()
        self.assertEqual(result, 1)
        self.assertIn("System firewall modification must be disabled", output)
    @patch(
        "ids.validate_project.run_health_check",
        return_value={"status": "degraded"},
    )
    @patch("ids.validate_project.IDSManager")
    @patch("ids.validate_project.load_config", return_value=VALID_CONFIG)
    def test_degraded_health_fails(
        self, mock_load, mock_manager, mock_health
    ):
        result, output = self.run_validation()
        self.assertEqual(result, 1)
        self.assertIn("Health check did not report healthy status", output)
    @patch(
        "ids.validate_project.load_config",
        side_effect=ValueError("Invalid configuration"),
    )
    def test_configuration_error_returns_failure(self, mock_load):
        result, output = self.run_validation()
        self.assertEqual(result, 1)
        self.assertIn("Validation error", output)
if __name__ == "__main__":
    unittest.main()