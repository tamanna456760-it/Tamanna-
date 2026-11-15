"""Safe Coding Assistant module backed by Tamanna's existing model capability layer.

This module only creates text proposals and analyses. It never executes code,
runs shell commands, writes project files, or deploys generated changes.
"""
from __future__ import annotations

from typing import Any


class CodingAssistantModule:
    """Expose the existing code-generation workflows through a stable module API."""

    ACTIONS = ("generate", "complete", "debug", "explain", "review", "refactor")

    def __init__(self, assistant: Any) -> None:
        self.assistant = assistant

    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run one allow-listed coding workflow using caller-supplied text only."""
        action = str(action or "").strip().lower()
        if action not in self.ACTIONS:
            raise ValueError(f"Unsupported coding action: {action or 'empty'}")
        if not isinstance(payload, dict):
            raise ValueError("Coding request payload must be an object")

        language = str(payload.get("language") or "auto").strip()[:80]
        project_context = str(payload.get("project_context") or "")
        if len(project_context) > 8000:
            raise ValueError("Project context exceeds 8000 characters")

        if action == "generate":
            feature = str(payload.get("feature") or "").strip()
            if not feature:
                raise ValueError("feature is required")
            requirements = payload.get("requirements") or []
            if not isinstance(requirements, list) or len(requirements) > 20:
                raise ValueError("requirements must be a list of at most 20 items")
            if any(not isinstance(item, str) or len(item) > 500 for item in requirements):
                raise ValueError("Each requirement must be text up to 500 characters")
            return await self.assistant.generate_code(
                feature,
                language=language or "Python",
                framework=str(payload.get("framework") or "")[:100],
                project_context=project_context,
                requirements=requirements,
            )

        if action == "complete":
            code_prefix = str(payload.get("code_prefix") or "")
            if not code_prefix.strip():
                raise ValueError("code_prefix is required")
            if len(code_prefix) > 20000:
                raise ValueError("code_prefix exceeds 20000 characters")
            return await self.assistant.complete_code(
                code_prefix,
                language=language,
                instruction=str(payload.get("instruction") or "")[:2000],
                project_context=project_context,
            )

        if action == "debug":
            error_report = str(payload.get("error_report") or "").strip()
            if not error_report:
                raise ValueError("error_report is required")
            return await self.assistant.debug_code(
                error_report,
                source_code=str(payload.get("source_code") or "")[:40000],
                runtime=str(payload.get("runtime") or "")[:200],
                expected_behavior=str(payload.get("expected_behavior") or "")[:2000],
                actual_behavior=str(payload.get("actual_behavior") or "")[:2000],
            )

        code = str(payload.get("code") or "")
        if not code.strip():
            raise ValueError("code is required")
        if len(code) > 40000:
            raise ValueError("code exceeds 40000 characters")

        tasks = {
            "explain": "Explain syntax, structure, control flow, and logic",
            "review": "Review for correctness, edge cases, maintainability, and security; separate evidence from hypotheses",
            "refactor": "Propose a behavior-preserving refactor and explain compatibility risks",
        }
        return await self.assistant.analyze_code(
            code,
            language=language,
            task=tasks[action],
            file_path=str(payload.get("file_path") or "")[:500],
            related_context=project_context,
        )


__all__ = ["CodingAssistantModule"]
