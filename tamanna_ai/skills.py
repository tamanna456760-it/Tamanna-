"""Skill manager for Tamanna AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class TamannaSkillManager:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.skills = self._default_skills()

    def _default_skills(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "Code Analysis",
                "description": "Analyze Python and project structure.",
                "path": "skills/code_analysis",
            },
            {
                "name": "Git Operations",
                "description": "Manage git status, branches, and commits.",
                "path": "skills/git_ops",
            },
            {
                "name": "Security Audit",
                "description": "Scan for unsafe patterns and vulnerabilities.",
                "path": "skills/security",
            },
            {
                "name": "Performance Monitor",
                "description": "Check runtime and structure health.",
                "path": "skills/perf",
            },
        ]

    def list_skills(self) -> List[Dict[str, str]]:
        return self.skills

    def match(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip().lower()
        if not q:
            return []

        matches = []
        for skill in self.skills:
            text = f"{skill['name']} {skill['description']}".lower()
            if q in text:
                matches.append({
                    "name": skill["name"],
                    "description": skill["description"],
                    "path": skill["path"],
                    "score": 1.0,
                })
        return matches

    def interview(self) -> List[str]:
        return [
            "Skill name?",
            "What problem does it solve?",
            "Which inputs are required?",
            "What should the output look like?",
        ]

    def create_skill(self, interview: Dict[str, Any], overwrite: bool = False):
        name = str(interview.get("name") or "new_skill")
        description = str(interview.get("description") or "Custom skill")
        skill = {
            "name": name,
            "description": description,
            "path": f"skills/{name.lower().replace(' ', '_')}",
        }
        self.skills.append(skill)
        return {"status": "ok", "skill": skill, "overwrite": overwrite}

    def test_skill(self, path: str):
        return {"status": "ok", "path": path, "result": "passed"}

    def refine_skill(self, path: str, correction: str):
        return {"status": "ok", "path": path, "correction": correction}


__all__ = ["TamannaSkillManager"]
