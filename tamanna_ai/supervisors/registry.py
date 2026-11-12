"""Hierarchical, policy-bounded supervisors for every tracked repository file.

This module defines routing metadata only. It does not spawn independent LLMs,
grant permissions, execute commands, or deploy changes.
"""
from __future__ import annotations

import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, List

SPECIALISTS = (
    ("architecture", "Architecture and design consistency"),
    ("implementation", "Implementation and code quality"),
    ("testing", "Tests, regression checks, and build validation"),
    ("security", "Security, privacy, and permission review"),
    ("operations", "Runtime health, reliability, and recovery review"),
)

SECTION_RULES = (
    ((".github/",), "ci", "CI and automation"),
    (("tamanna_ai/authentication/",), "identity", "Authentication and access control"),
    (("tamanna_ai/security/", "tamanna_ai/cyber_security/", "tamanna_ai/security_training/", "app_security/", "endpoint_security/", "waf/"), "security", "Security and compliance"),
    (("tamanna_ai/agents/", "tamanna_ai/brain/", "tamanna_ai/ai_core/", "tamanna_ai/planner/"), "intelligence", "AI agents, reasoning, and planning"),
    (("tamanna_ai/integrations/",), "integrations", "Model and external integrations"),
    (("tamanna_ai/api/", "tamanna_ai/web/", "tamanna_ai/dashboard/", "static/", "css/", "js/"), "interface", "API, web, and user interface"),
    (("tamanna_ai/memory/", "tamanna_ai/knowledge/", "tamanna_ai/learning/", "data/"), "knowledge", "Memory, learning, and data"),
    (("tamanna_ai/backup/", "tamanna_ai/persistence/"), "storage", "Persistence and backup"),
    (("tamanna_ai/testing/", "tamanna_ai/auto_tester/", "tests/"), "quality", "Testing and quality assurance"),
    (("tamanna_ai/scanner/", "tamanna_ai/scanners/", "tamanna_ai/analysis/", "tamanna_ai/code_analyzer/", "tamanna_ai/code_manager/"), "analysis", "Analysis, scanning, and code review"),
    (("deploy/", "cloudflare/", "firewall/", "tamanna-server/", "bd-king-r7/"), "infrastructure", "Deployment and infrastructure"),
    (("docs/", "tamanna_ai/docs/"), "documentation", "Documentation and knowledge resources"),
    (("tamanna_ai/workflows/", "tamanna_ai/workflow_engine/"), "workflow", "Workflow orchestration"),
    (("tamanna_ai/tools/", "tamanna_ai/plugins/", "tamanna_ai/plugin_manager/"), "extensions", "Tools and plugin ecosystem"),
    (("android/", "tamanna-ai-app/"), "mobile", "Mobile application"),
    (("tamanna_ai/",), "tamanna_core", "Tamanna AI core services"),
)

def _section_for(path: str):
    normalized = path.replace(os.sep, "/").lstrip("./")
    for prefixes, key, label in SECTION_RULES:
        if normalized.startswith(prefixes):
            return key, label
    first = normalized.split("/", 1)[0] if "/" in normalized else "root"
    return "repo_" + (first or "root").replace(".", "_").replace("-", "_"), (
        "Repository section: " + (first or "root")
    )

def _tracked_paths(root: Path) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=str(root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            return sorted(p for p in result.stdout.decode("utf-8", "replace").split("\0") if p)
    except (OSError, subprocess.SubprocessError):
        pass
    excluded = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    paths = []
    for current, dirs, files in os.walk(str(root)):
        dirs[:] = [d for d in dirs if d not in excluded]
        for filename in files:
            absolute = Path(current) / filename
            paths.append(absolute.relative_to(root).as_posix())
    return sorted(paths)

def build_supervisor_registry(repository_root: str | Path) -> dict:
    """Return a deterministic owner + five-specialist review map for each file."""
    root = Path(repository_root).resolve()
    sections: Dict[str, dict] = {}
    file_owners = {}
    for relative_path in _tracked_paths(root):
        section_id, label = _section_for(relative_path)
        section = sections.setdefault(section_id, {
            "id": section_id,
            "name": label,
            "supervisor_id": "supervisor_" + section_id,
            "specialists": [
                {
                    "id": section_id + "_" + role,
                    "role": role,
                    "responsibility": responsibility,
                }
                for role, responsibility in SPECIALISTS
            ],
            "file_count": 0,
        })
        section["file_count"] += 1
        file_owners[relative_path] = {
            "section_supervisor": section["supervisor_id"],
            "specialist_reviewers": [agent["id"] for agent in section["specialists"]],
        }
    return {
        "mode": "registry_only",
        "repository": root.name,
        "section_count": len(sections),
        "tracked_file_count": len(file_owners),
        "specialists_per_section": len(SPECIALISTS),
        "sections": sections,
        "file_owners": file_owners,
        "permissions": {
            "read_only_by_default": True,
            "sandbox_changes_require_admin_enablement": True,
            "production_changes_require_separate_human_approval": True,
            "self_grant_permissions": False,
            "disable_security_controls": False,
        },
    }

__all__ = ["build_supervisor_registry", "SPECIALISTS"]
