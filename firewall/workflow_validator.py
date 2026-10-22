"""Read-only validator for the Tamanna AI Firewall GitHub Actions workflow.
Owner: HM INSAN ALI
This module checks selected security settings without modifying files.
"""
from pathlib import Path
DEFAULT_WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "tamanna-firewall-tests.yml"
)
def validate_workflow(workflow_path=DEFAULT_WORKFLOW):
    """Return validation results for the configured workflow."""
    path = Path(workflow_path)
    errors = []
    warnings = []
    if not path.is_file():
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "valid": False,
            "errors": [f"Workflow file not found: {path}"],
            "warnings": [],
            "workflow_path": str(path),
        }
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "valid": False,
            "errors": [f"Cannot read workflow: {exc}"],
            "warnings": [],
            "workflow_path": str(path),
        }
    required = [
        "permissions:",
        "contents: read",
        "jobs:",
        "actions/checkout@v4",
        "actions/setup-python@v5",
        "python -m firewall.run_tests",
    ]
    for item in required:
        if item not in content:
            errors.append(f"Missing required workflow setting: {item}")
    if "contents: write" in content:
        errors.append("Workflow requests contents: write permission.")
    if "pull_request_target:" in content:
        warnings.append(
            "Review pull_request_target carefully before running "
            "untrusted pull-request code."
        )
    if "timeout-minutes:" not in content:
        warnings.append("No explicit job timeout was found.")
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "workflow_path": str(path),
    }
if __name__ == "__main__":
    import json
    print(
        json.dumps(
            validate_workflow(),
            indent=2,
            ensure_ascii=False,
        )
    )