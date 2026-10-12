"""
Tamanna AI Firewall - Doctor Report
Owner: HM INSAN ALI
Runs read-only diagnostics and saves a JSON report.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from firewall.doctor import run_diagnostics
def generate_doctor_report(base_dir=None):
    """Generate a diagnostic report without changing firewall rules."""
    root = Path(base_dir) if base_dir else Path(__file__).parent
    result = run_diagnostics(root)
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "report_type": "firewall_doctor",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diagnostics": result,
        "system_firewall_modified": False,
    }
def save_doctor_report(output_path, base_dir=None):
    """Atomically save the diagnostic report."""
    destination = Path(output_path)
    temporary = destination.with_name(destination.name + ".tmp")
    report = generate_doctor_report(base_dir)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2)
            file.write("\n")
        temporary.replace(destination)
        report["saved_to"] = str(destination)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        report["save_error"] = str(exc)
    return report
if __name__ == "__main__":
    root = Path(__file__).parent
    output = root / "reports" / "doctor_report.json"
    result = save_doctor_report(output)
    print(json.dumps(result, indent=2))
    if result.get("save_error"):
        raise SystemExit(2)
    status = result["diagnostics"]["status"]
    raise SystemExit(0 if status == "OK" else 1)