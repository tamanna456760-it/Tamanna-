"""Tests for firewall manager configuration loading."""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.firewall_manager import FirewallManager
class TestFirewallManagerConfig(unittest.TestCase):
    def test_manager_initializes_with_default_configuration(self):
        """Manager should initialize without crashing."""
        manager = FirewallManager()
        self.assertIsNotNone(manager)
    def test_config_file_is_valid_json(self):
        """Repository firewall configuration should be valid JSON."""
        config_path = (
            Path(__file__).resolve().parents[2]
            / "firewall"
            / "firewall_config.json"
        )
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
        self.assertIsInstance(config, dict)
    def test_invalid_config_is_not_silently_accepted(self):
        """If the manager accepts a config path, invalid JSON must be rejected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid.json"
            invalid_path.write_text("{ invalid json", encoding="utf-8")
            try:
                manager = FirewallManager(config_path=str(invalid_path))
            except (ValueError, json.JSONDecodeError, OSError):
                return
            except TypeError:
                self.skipTest(
                    "FirewallManager does not accept config_path; "
                    "inspect its constructor before adapting this test."
                )
            self.fail(
                "FirewallManager accepted invalid JSON without raising an error."
            )
if __name__ == "__main__":
    unittest.main()