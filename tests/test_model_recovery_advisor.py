import unittest

from tamanna_ai.integrations.recovery_advisor import build_recovery_report


class RecoveryAdvisorTests(unittest.TestCase):
    def test_reports_runtime_unreachable_with_safe_steps(self):
        report = build_recovery_report(
            provider="ollama", selected_model="qwen2.5:7b",
            installed_models=[], runtime_error="runtime_unreachable",
            host_metrics={},
        )
        self.assertEqual(report["code"], "ollama_unreachable")
        self.assertEqual(report["status"], "offline")
        self.assertFalse(report["automatic_changes"])
        self.assertTrue(report["actions"])

    def test_warns_for_missing_selected_model_and_high_memory_pressure(self):
        report = build_recovery_report(
            provider="ollama", selected_model="missing:1b",
            installed_models=["qwen2.5:7b"], runtime_error=None,
            host_metrics={"memory": {"usage_percent": 93}, "disk": {"usage_percent": 96}},
        )
        self.assertEqual(report["code"], "selected_model_missing")
        self.assertEqual(report["status"], "attention")
        self.assertGreaterEqual(len(report["actions"]), 3)

    def test_reports_healthy_runtime(self):
        report = build_recovery_report(
            provider="ollama", selected_model="qwen2.5:7b",
            installed_models=["qwen2.5:7b"], runtime_error=None,
            host_metrics={},
        )
        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["code"], "runtime_available")


if __name__ == "__main__":
    unittest.main()
