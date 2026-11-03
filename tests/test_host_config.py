"""Regression tests for the Tamanna Host profile."""
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "host.toml"


class TamannaHostConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG_PATH.open("rb") as stream:
            cls.config = tomllib.load(stream)

    def test_display_and_machine_host_names(self):
        self.assertEqual(self.config["host"]["name"], "Tamanna")
        self.assertEqual(self.config["host"]["hostname"], "tamanna")

    def test_application_endpoint(self):
        app = self.config["application"]
        self.assertEqual(app["name"], "Tamanna AI")
        self.assertEqual(app["backend"], "FastAPI")
        self.assertEqual(app["bind_host"], "127.0.0.1")
        self.assertEqual(app["port"], 8000)
        self.assertEqual(app["health_path"], "/health")

    def test_deployment_settings(self):
        deployment = self.config["deployment"]
        self.assertEqual(deployment["provider"], "self-hosted")
        self.assertEqual(deployment["container_runtime"], "docker")
        self.assertEqual(deployment["reverse_proxy"], "nginx")
        self.assertTrue(deployment["tls_required"])

    def test_no_secrets_are_stored_in_host_profile(self):
        security = self.config["security"]
        self.assertFalse(security["secrets_in_repository"])
        self.assertEqual(security["environment_file"], ".env")


if __name__ == "__main__":
    unittest.main()
