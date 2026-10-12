"""YAML syntax checker for Tamanna AI Firewall workflows.
Owner: HM INSAN ALI
Read-only: does not modify workflow files or firewall rules.
"""
import json
import sys
from pathlib import Path
WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "tamanna-firewall-tests.yml"
)
def check_yaml(workflow_path=WORKFLOW_PATH):
    path = Path(workflow_path)
    result = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "workflow_path": str(path),
        "valid": False,
        "error": None,
        "system_firewall_modified": False,
    }
    if not path.is_file():
        result["error"] = "Workflow file not found."
        return result
    try:
        import yaml
    except ImportError:
        result["error"] = (
            "PyYAML is not installed. Install it with: "
            "python3 -m pip install PyYAML"
        )
        return result
    try:
        with path.open("r", encoding="utf-8") as file:
            parsed = yaml.safe_load(file)
        if not isinstance(parsed, dict):
            result["error"] = "Workflow YAML must contain a mapping."
            return result
        if "jobs" not in parsed or not isinstance(parsed["jobs"], dict):
            result["error"] = "Workflow must define a jobs mapping."
            return result
        result["valid"] = True
    except (yaml.YAMLError, OSError, UnicodeError) as exc:
        result["error"] = str(exc)
    return result
def main():
    result = check_yaml()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["valid"]:
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())