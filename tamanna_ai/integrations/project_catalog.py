"""Curated catalogue of optional AI projects integrated conceptually into Tamanna.

This module intentionally does not import or execute third-party project code.
Each upstream source must be identified, license-reviewed, pinned, and security
reviewed before an adapter is marked available.
"""
from __future__ import annotations

from typing import Any


_PROJECTS: tuple[dict[str, Any], ...] = (
    {
        "id": "autogen",
        "name": "AutoGen",
        "feature": "multi_agent_coordination",
        "description": "Coordinate specialist agents through explicit, bounded task plans.",
        "memory_topics": ("agent roles", "message routing", "human approval", "termination rules"),
        "upstream_commit": "027ecf0a379bcc1d09956d46d12d44a3ad9cee14",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "cli",
        "name": "CLI",
        "feature": "safe_cli_interface",
        "description": "Provide a typed, allow-listed command interface; no arbitrary shell execution.",
        "memory_topics": ("command help", "allow-list", "permissions", "audit logs"),
        "upstream_commit": "4ed0e4e65dfd447668a775cefb65312c8bc980c7",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "crewai",
        "name": "CrewAI",
        "feature": "agent_task_planning",
        "description": "Represent tasks, roles, dependencies, and review gates for agent workflows.",
        "memory_topics": ("agents", "tasks", "delegation", "review gates"),
        "upstream_commit": "fb8e93be25d97776cf18368c3ac56e7ac69661b9",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "dify",
        "name": "Dify",
        "feature": "workflow_orchestration",
        "description": "Connect approved workflow definitions through documented APIs.",
        "memory_topics": ("workflow definitions", "triggers", "approvals", "webhooks"),
        "upstream_commit": "d97a29317c427a3a4ffcbb78ced3e053faad0af8",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "langchain",
        "name": "LangChain",
        "feature": "llm_retrieval_pipelines",
        "description": "Build replaceable model and retrieval pipelines with source attribution.",
        "memory_topics": ("retrievers", "document loaders", "prompt templates", "citations"),
        "upstream_commit": "cdafe607af6ba4c0ae8c73575488f74ce7962da1",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "n8n",
        "name": "n8n",
        "feature": "workflow_automation",
        "description": "Trigger approved external automations through scoped credentials and webhooks.",
        "memory_topics": ("workflow inventory", "webhook contracts", "run status", "retry policy"),
        "upstream_commit": "0db6a4b7d82ce1424a4f044bb52cb02d12ce67d7",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "open-webui",
        "name": "Open WebUI",
        "feature": "chat_ui_reference",
        "description": "Use as a reference for optional chat UI interoperability, not a bundled UI dependency.",
        "memory_topics": ("chat interface", "provider settings", "conversation UX", "accessibility"),
        "upstream_commit": "ecd48e2f718220a6400ecf49eafd4867a38feb10",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "power-systems-cli",
        "name": "Power Systems CLI",
        "feature": "system_operations",
        "description": "Model safe system status and diagnostics; privileged changes require approval.",
        "memory_topics": ("health checks", "diagnostics", "service status", "approval policy"),
        "upstream_commit": "4ed0e4e65dfd447668a775cefb65312c8bc980c7",
        "source_url": None,
        "status": "source_unverified",
    },
    {
        "id": "tamanna-project-reference",
        "name": "Tamanna project reference",
        "feature": "internal_project_knowledge",
        "description": "Preserve the pinned project reference as provenance for later source recovery.",
        "memory_topics": ("architecture", "module map", "integration decisions", "project history"),
        "upstream_commit": "fafae64c865e1789aa40523d2dd36be09e056080",
        "source_url": None,
        "status": "source_unverified",
    },
)


def list_projects() -> list[dict[str, Any]]:
    """Return safe, JSON-serializable project metadata without mutable internals."""
    return [
        {**project, "memory_topics": list(project["memory_topics"])}
        for project in _PROJECTS
    ]


def get_project(project_id: str) -> dict[str, Any] | None:
    """Find one project by its stable identifier."""
    normalized = str(project_id).strip().lower()
    for project in _PROJECTS:
        if project["id"] == normalized:
            return {**project, "memory_topics": list(project["memory_topics"])}
    return None


def search_project_knowledge(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Lexically search the curated project catalogue; this is not user memory."""
    terms = {term for term in str(query).lower().split() if term}
    if not terms:
        return []
    try:
        bounded_limit = max(1, min(int(limit), 20))
    except (TypeError, ValueError):
        bounded_limit = 5

    ranked: list[tuple[int, dict[str, Any]]] = []
    for project in _PROJECTS:
        searchable = " ".join(
            (
                project["id"],
                project["name"],
                project["feature"],
                project["description"],
                *project["memory_topics"],
            )
        ).lower()
        score = sum(term in searchable for term in terms)
        if score:
            ranked.append((score, project))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [
        {
            **project,
            "memory_topics": list(project["memory_topics"]),
            "match_score": score,
        }
        for score, project in ranked[:bounded_limit]
    ]
