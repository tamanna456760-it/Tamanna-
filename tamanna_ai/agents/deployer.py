"""Tamanna AI Deployment Preflight Agent.
This module validates deployment prerequisites.
It intentionally does not execute deployment commands.
"""
import shutil
from pathlib import Path
from typing import Iterable, Optional
class DeployerAgent:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
    def preflight(
        self,
        required_files: Optional[Iterable[str]] = None,
        required_commands: Optional[Iterable[str]] = None,
    ) -> dict:
        files = list(required_files or ["Main.py", "main.py"])
        commands = list(required_commands or [])
        missing_files = []
        unsafe_paths = []
        for relative_path in files:
            target = (self.project_root / relative_path).resolve()
            if target != self.project_root and self.project_root not in target.parents:
                unsafe_paths.append(relative_path)
                continue
            if not target.is_file():
                missing_files.append(relative_path)
        missing_commands = [
            command for command in commands
            if not shutil.which(command)
        ]
        passed = not missing_files and not missing_commands and not unsafe_paths
        return {
            "success": passed,
            "status": "ready_for_review" if passed else "blocked",
            "project_root": str(self.project_root),
            "missing_files": missing_files,
            "missing_commands": missing_commands,
            "unsafe_paths": unsafe_paths,
            "deployment_executed": False,
        }
if __name__ == "__main__":
    agent = DeployerAgent()
    print(agent.preflight())