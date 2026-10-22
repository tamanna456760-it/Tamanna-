"""Tests for Tamanna AI firewall configuration."""
import json
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "firewall" / "firewall_config.json"
class TestFirewallConfig(unittest.TestCase):
    def test_config_file_exists(self):
        """Firewall configuration file should exist."""
        self.assertTrue(
            CONFIG_PATH.is_file(),
            f"Missing configuration file: {CONFIG_PATH}",
        )
    def test_config_contains_valid_json(self):
        """Configuration should contain valid JSON."""
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
        self.assertIsInstance(config, dict)
    def test_config_uses_safe_default_mode(self):
        """New configuration should use audit-only mode."""
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
        self.assertEqual(config.get("mode"), "audit_only")
    def test_system_firewall_changes_require_approval(self):
        """Configuration must not enable unapproved system-rule changes."""
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
        integration = config.get("system_firewall", {})
        if isinstance(integration, dict):
            self.assertFalse(
                integration.get("modify_system_rules", False),
                "System firewall rule changes must remain disabled by default.",
            )
if __name__ == "__main__":
    unittest.main()