# Digital forensics for incident response
import json
import os
from pathlib import Path


class ForensicAnalyzer:
    def __init__(self, evidence_path):
        self.evidence_path = Path(evidence_path)
        self.findings = []

    def collect_system_info(self):
        """Collect system information for forensic analysis"""
        system_info = {
            "hostname": os.uname().nodename,
            "system": os.uname().sysname,
            "current_user": os.getenv("USER"),
            "working_directory": os.getcwd(),
        }
        return system_info

    def analyze_file_system(self):
        """Analyze file system for suspicious files"""
        suspicious_extensions = [".exe", ".bat", ".sh", ".py"]
        suspicious_files = []

        for file_path in self.evidence_path.rglob("*"):
            if file_path.suffix.lower() in suspicious_extensions:
                file_info = {
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                }
                suspicious_files.append(file_info)

        return suspicious_files

    def generate_report(self):
        """Generate forensic analysis report"""
        report = {
            "system_info": self.collect_system_info(),
            "suspicious_files": self.analyze_file_system(),
            "analysis_date": datetime.now().isoformat(),
        }

        with open("forensic_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report
