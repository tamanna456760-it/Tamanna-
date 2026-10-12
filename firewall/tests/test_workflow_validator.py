"""Tests for the Tamanna AI Firewall workflow validator.
Owner: HM INSAN ALI
"""
import tempfile
import unittest
from pathlib import Path
from firewall.workflow_validator import validate_workflow
class TestWorkflowValidator(unittest.TestCase):
    def test_missing_workflow_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.yml"
            result = validate_workflow(missing)
            self.assertFalse(result["valid"])
            self.assertTrue(result["errors"])
    def test_valid_workflow_passes_required_checks(self):
        content = """\
name: Tamanna AI Firewall Tests
permissions:
  contents: read
jobs:
  firewall-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python -m firewall.run_tests
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "workflow.yml"
            workflow.write_text(content, encoding="utf-8")
            result = validate_workflow(workflow)
            self.assertTrue(result["valid"])
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["warnings"], [])
    def test_write_permission_is_rejected(self):
        content = """\
permissions:
  contents: read
  contents: write
jobs:
  firewall-tests:
    uses: actions/checkout@v4
    run: python -m firewall.run_tests
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "workflow.yml"
            workflow.write_text(content, encoding="utf-8")
            result = validate_workflow(workflow)
            self.assertFalse(result["valid"])
            self.assertTrue(
                any("contents: write" in error
                    for error in result["errors"])
            )
    def test_missing_timeout_produces_warning(self):
        content = """\
permissions:
  contents: read
jobs:
  firewall-tests:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python -m firewall.run_tests
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Path(temp_dir) / "workflow.yml"
            workflow.write_text(content, encoding="utf-8")
            result = validate_workflow(workflow)
            self.assertTrue(result["valid"])
            self.assertTrue(
                any("timeout" in warning.lower()
                    for warning in result["warnings"])
            )
if __name__ == "__main__":
    unittest.main()