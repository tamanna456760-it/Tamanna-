"""Tests for the Tamanna AI Firewall GitHub Actions workflow.
Owner: HM INSAN ALI
"""
import unittest
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_FILE = (
    REPO_ROOT
    / ".github"
    / "workflows"
    / "tamanna-firewall-tests.yml"
)
class TestWorkflowConfig(unittest.TestCase):
    def test_workflow_file_exists(self):
        self.assertTrue(
            WORKFLOW_FILE.is_file(),
            f"Workflow file not found: {WORKFLOW_FILE}",
        )
    def test_workflow_contains_required_jobs_and_steps(self):
        if not WORKFLOW_FILE.is_file():
            self.skipTest("Workflow file has not been created")
        content = WORKFLOW_FILE.read_text(encoding="utf-8")
        required_text = [
            "name: Tamanna AI Firewall Tests",
            "jobs:",
            "firewall-tests:",
            "actions/checkout@v4",
            "actions/setup-python@v5",
            "python -m firewall.run_tests",
            "permissions:",
            "contents: read",
        ]
        for item in required_text:
            with self.subTest(required_text=item):
                self.assertIn(item, content)
    def test_workflow_does_not_request_write_permissions(self):
        if not WORKFLOW_FILE.is_file():
            self.skipTest("Workflow file has not been created")
        content = WORKFLOW_FILE.read_text(encoding="utf-8")
        self.assertIn("contents: read", content)
        self.assertNotIn("contents: write", content)
if __name__ == "__main__":
    unittest.main()