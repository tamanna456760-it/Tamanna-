"""Tests for Tamanna AI Firewall workflow YAML checker.
Owner: HM INSAN ALI
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from firewall.workflow_yaml_check import check_yaml
class TestWorkflowYamlCheck(unittest.TestCase):
    def test_missing_file_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.yml"
            result = check_yaml(missing)
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Workflow file not found.")
        self.assertFalse(result["system_firewall_modified"])
    def test_valid_yaml_workflow(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML is not installed")
        content = """
name: Tamanna AI Firewall Tests
permissions:
  contents: read
jobs:
  firewall-tests:
    runs-on: ubuntu-latest
    steps:
      - run: python -m firewall.run_tests
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "workflow.yml"
            workflow.write_text(content, encoding="utf-8")
            result = check_yaml(workflow)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["error"])
    def test_invalid_yaml_is_rejected(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML is not installed")
        content = "jobs:\n  firewall-tests: [invalid\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "broken.yml"
            workflow.write_text(content, encoding="utf-8")
            result = check_yaml(workflow)
        self.assertFalse(result["valid"])
        self.assertIsNotNone(result["error"])
    def test_missing_jobs_is_rejected(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML is not installed")
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "no-jobs.yml"
            workflow.write_text("name: Example\n", encoding="utf-8")
            result = check_yaml(workflow)
        self.assertFalse(result["valid"])
        self.assertIn("jobs", result["error"])
    @patch(
        "firewall.workflow_yaml_check.WORKFLOW_PATH",
        Path("/path/that/does/not/exist/workflow.yml"),
    )
    def test_default_workflow_path_can_be_overridden(self):
        # Explicit paths are the primary supported test interface.
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "workflow.yml"
            workflow.write_text("jobs: {}\n", encoding="utf-8")
            result = check_yaml(workflow)
        self.assertTrue(result["valid"])
if __name__ == "__main__":
    unittest.main()