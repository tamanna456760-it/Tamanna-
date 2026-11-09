import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_env import validate_env


class ValidateEnvTests(unittest.TestCase):
    def write_env(self, directory, values):
        path = Path(directory) / ".env"
        path.write_text("\n".join(f"{key}={value}" for key, value in values.items()), encoding="utf-8")
        return path

    def test_local_ollama_configuration_does_not_require_hosted_api_key(self):
        values = {
            "TAMANNA_ENV": "production",
            "TAMANNA_MODEL_PROVIDER": "ollama",
            "TAMANNA_OLLAMA_URL": "http://127.0.0.1:11434",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
            "TAMANNA_SESSION_SECRET": "T4manna-Env-Test-Key-2026-Strong-9f3a7c2e6b8d",
            "TAMANNA_DATABASE_URL": "sqlite:///data/tamanna.sqlite3",
            "TAMANNA_CORS_ORIGINS": "https://www.bd-king-r7.com",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            report = validate_env(self.write_env(directory, values), strict=True)
        self.assertEqual(report["status"], "PASS")
        self.assertNotIn("gemini_api_key", report["checks"])
        self.assertFalse(report["secrets_printed"])

    def test_strict_mode_rejects_repeated_session_secret(self):
        values = {
            "TAMANNA_ENV": "production",
            "TAMANNA_MODEL_PROVIDER": "ollama",
            "TAMANNA_OLLAMA_URL": "http://127.0.0.1:11434",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
            "TAMANNA_SESSION_SECRET": "s" * 48,
            "TAMANNA_DATABASE_URL": "sqlite:///data/tamanna.sqlite3",
            "TAMANNA_CORS_ORIGINS": "https://www.bd-king-r7.com",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            report = validate_env(self.write_env(directory, values), strict=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("session_secret", report["missing"])

    def test_strict_mode_requires_session_secret(self):
        values = {
            "TAMANNA_MODEL_PROVIDER": "ollama",
            "TAMANNA_OLLAMA_URL": "http://127.0.0.1:11434",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
            "TAMANNA_CORS_ORIGINS": "http://localhost:8001",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            report = validate_env(self.write_env(directory, values), strict=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("session_secret", report["missing"])

    def test_production_rejects_insecure_cookie_or_http_cors_origin(self):
        values = {
            "TAMANNA_ENV": "production",
            "TAMANNA_MODEL_PROVIDER": "ollama",
            "TAMANNA_OLLAMA_URL": "http://127.0.0.1:11434",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
            "TAMANNA_SESSION_SECRET": "T4manna-Env-Test-Key-2026-Strong-9f3a7c2e6b8d",
            "TAMANNA_CORS_ORIGINS": "https://www.bd-king-r7.com,http://localhost:8001",
            "TAMANNA_COOKIE_SECURE": "0",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            report = validate_env(self.write_env(directory, values), strict=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("production_transport_security", report["missing"])

    def test_mock_provider_is_allowed_only_in_test_environment(self):
        base = {
            "TAMANNA_MODEL_PROVIDER": "mock",
            "TAMANNA_SESSION_SECRET": "T4manna-Env-Test-Key-2026-Strong-9f3a7c2e6b8d",
            "TAMANNA_CORS_ORIGINS": "http://localhost:8001",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            production = validate_env(self.write_env(directory, {**base, "TAMANNA_ENV": "production"}), strict=True)
        self.assertEqual(production["status"], "FAIL")
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            testing = validate_env(self.write_env(directory, {**base, "TAMANNA_ENV": "test"}), strict=True)
        self.assertEqual(testing["status"], "PASS")

    def test_invalid_ollama_url_fails_strict_validation(self):
        values = {
            "TAMANNA_MODEL_PROVIDER": "ollama",
            "TAMANNA_OLLAMA_URL": "not-a-url",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
            "TAMANNA_SESSION_SECRET": "T4manna-Env-Test-Key-2026-Strong-9f3a7c2e6b8d",
            "TAMANNA_CORS_ORIGINS": "http://localhost:8001",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            report = validate_env(self.write_env(directory, values), strict=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("model_provider", report["missing"])


if __name__ == "__main__":
    unittest.main()
