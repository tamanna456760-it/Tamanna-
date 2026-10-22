"""Security checks for Tamanna AI firewall configuration."""
import json
import unittest
from pathlib import Path
CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "firewall"
    / "firewall_config.json"
)
class TestFirewallConfigSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            cls.config = json.load(file)
    def test_configuration_is_a_json_object(self):
        self.assertIsInstance(self.config, dict)
    def test_default_mode_is_audit_only(self):
        self.assertEqual(self.config.get("mode"), "audit_only")
    def test_default_policy_is_deny(self):
        self.assertEqual(self.config.get("default_policy"), "deny")
    def test_system_rule_modification_is_disabled(self):
        """OS firewall changes must not be enabled by default."""
        integration = self.config.get("system_firewall", {})
        if not isinstance(integration, dict):
            self.fail("system_firewall configuration must be an object")
        self.assertIs(
            integration.get("modify_system_rules", False),
            False,
            "System firewall changes must remain disabled by default.",
        )
    def test_secret_values_are_not_hardcoded(self):
        """Reject obvious placeholder secrets in common configuration fields."""
        suspicious_names = {
            "password",
            "secret",
            "api_key",
            "access_token",
            "orchestrator_token",
        }
        def inspect(value, path="config"):
            if isinstance(value, dict):
                for key, item in value.items():
                    key_lower = str(key).lower()
                    if key_lower in suspicious_names and isinstance(item, str):
                        normalized = item.strip().lower()
                        if normalized in {
                            "change-this-token",
                            "changeme",
                            "your-secret-here",
                            "replace-me",
                        }:
                            self.fail(
                                f"Replace placeholder secret at {path}.{key}"
                            )
                    inspect(item, f"{path}.{key}")
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    inspect(item, f"{path}[{index}]")
        inspect(self.config)
if __name__ == "__main__":
    unittest.main()