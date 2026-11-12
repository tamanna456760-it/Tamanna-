"""Policy-bounded supervisor teams and per-file ownership routing.

This module creates deterministic team definitions; it does not start LLM workers.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, List

SECTION_SPECIALISTS = (
    ("architecture", "Architecture and design consistency", "review_design"),
    ("implementation", "Create and upgrade code in an approved sandbox or branch", "propose_code_changes"),
    ("testing", "Run tests and validate regression/build evidence", "run_tests"),
    ("security", "Review security, privacy, and permission boundaries", "review_security"),
    ("operations", "Review runtime health, reliability, and recovery", "review_operations"),
)

DEFENSE_SPECIALISTS = (
    ("threat_detection", "Identify suspicious behavior and security events", "analyze_security_events"),
    ("hardening", "Review secure configuration and defensive controls", "propose_hardening"),
    ("vulnerability_management", "Triage dependency and code vulnerabilities", "triage_vulnerabilities"),
    ("incident_response", "Prepare containment and incident response recommendations", "recommend_incident_response"),
    ("recovery_integrity", "Verify backups, integrity, and recovery readiness", "verify_recovery"),
)

SERVER_SPECIALISTS = (
    ("health_monitor", "Monitor approved service and endpoint health checks", "observe_service_health"),
    ("deployment", "Prepare and validate deployment plans", "prepare_deployment"),
    ("infrastructure", "Review server, network, TLS, DNS, and configuration", "review_infrastructure"),
    ("backup_restore", "Validate backup and restore procedures", "verify_backup_restore"),
    ("reliability", "Analyze logs, capacity, uptime, and recovery runbooks", "analyze_reliability"),
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
    normalized = path.replace(os.sep, "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
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


def _team(team_id: str, name: str, specialists: tuple) -> dict:
    return {
        "id": team_id,
        "name": name,
        "supervisor_id": "supervisor_" + team_id,
        "specialists": [
            {
                "id": team_id + "_" + role,
                "role": role,
                "responsibility": responsibility,
                "capability": capability,
            }
            for role, responsibility, capability in specialists
        ],
        "specialists_count": len(specialists),
    }


def build_supervisor_registry(repository_root: str | Path) -> dict:
    """Build one section lead + five specialists and two cross-cutting teams."""
    root = Path(repository_root).resolve()
    sections: Dict[str, dict] = {}
    file_owners = {}

    defense_team = _team("defense", "Tamanna Defense and Security Team", DEFENSE_SPECIALISTS)
    server_team = _team("server_ops", "Tamanna Server Operations Team", SERVER_SPECIALISTS)

    for relative_path in _tracked_paths(root):
        section_id, label = _section_for(relative_path)
        section = sections.setdefault(
            section_id,
            _team(section_id, label, SECTION_SPECIALISTS),
        )
        section["file_count"] = section.get("file_count", 0) + 1

        normalized = relative_path.replace(os.sep, "/")
        defense_relevant = (
            section_id in {"identity", "security"}
            or any(part in normalized for part in ("security", "firewall", "waf", "auth"))
        )
        server_relevant = section_id == "infrastructure" or normalized.startswith(
            ("deploy/", "cloudflare/", "firewall/", "tamanna-server/", "bd-king-r7/")
        )
        file_owners[relative_path] = {
            "section_supervisor": section["supervisor_id"],
            "specialist_reviewers": [agent["id"] for agent in section["specialists"]],
            "defense_team": defense_team["id"] if defense_relevant else None,
            "server_operations_team": server_team["id"] if server_relevant else None,
            "code_change_policy": "sandbox_or_feature_branch_only",
        }

    return {
        "mode": "registry_only",
        "repository": root.name,
        "section_count": len(sections),
        "tracked_file_count": len(file_owners),
        "specialists_per_section": len(SECTION_SPECIALISTS),
        "sections": sections,
        "cross_cutting_teams": {
            "defense": defense_team,
            "server_operations": server_team,
        },
        "file_owners": file_owners,
        "permissions": {
            "read_only_by_default": True,
            "code_changes_require_admin_enabled_sandbox": True,
            "github_push_requires_scoped_credentials_and_approval": True,
            "production_changes_require_separate_human_approval": True,
            "self_grant_permissions": False,
            "disable_security_controls": False,
        },
        "runtime": {
            "workers_started": False,
            "reason": "A configured and authenticated model worker runtime is required.",
        },
    }


__all__ = [
    "build_supervisor_registry",
    "SECTION_SPECIALISTS",
    "DEFENSE_SPECIALISTS",
    "SERVER_SPECIALISTS",
]
