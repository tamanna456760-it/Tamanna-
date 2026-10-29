
"""Safe, minimal Advanced Code Builder for Tamanna AI.

Supports project discovery, planning, guarded file creation,
Python syntax checks, and compile checks.
"""

from __future__ import annotations

import ast
import compileall
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class BuildResult:
    ok: bool
    language: str
    files: list[str]
    checks: list[dict[str, Any]]
    errors: list[str]
    warnings: list[str]


class AdvancedCodeBuilder:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()

    def _safe_path(self, relative_path: str) -> Path:
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError("A relative file path is required.")

        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise ValueError("Absolute paths are not allowed.")

        target = (self.project_root / candidate).resolve()

        if target == self.project_root or self.project_root not in target.parents:
            raise ValueError("Path is outside the project directory.")

        return target

    def discover(self) -> dict[str, Any]:
        files = []
        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue
            if any(
                part in {".git", ".venv", "venv", "__pycache__", "node_modules"}
                for part in path.parts
            ):
                continue
            files.append(path.relative_to(self.project_root).as_posix())

        return {
            "ok": True,
            "project_root": str(self.project_root),
            "total_files": len(files),
            "files": sorted(files)[:500],
            "truncated": len(files) > 500,
        }

    def plan(self, request: str) -> list[dict[str, Any]]:
        request = str(request).strip()
        if not request:
            return []

        tasks = [
            "Inspect the requested change and affected files.",
            "Validate paths and required dependencies.",
            "Prepare the smallest safe implementation.",
            "Run available syntax checks.",
            "Review results before accepting the change.",
        ]
        return [
            {"step": i, "task": task, "status": "pending"}
            for i, task in enumerate(tasks, start=1)
        ]

    def build(
        self,
        files: list[dict[str, Any]],
        overwrite: bool = False,
    ) -> BuildResult:
        created: list[str] = []
        checks: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(files, list):
            return BuildResult(
                False, "unknown", [], [], ["files must be a list"], []
            )

        for item in files:
            if not isinstance(item, dict):
                errors.append("Each file entry must be an object.")
                continue

            relative_path = item.get("path")
            content = item.get("content")

            if not isinstance(content, str):
                errors.append(f"{relative_path}: content must be a string.")
                continue

            try:
                target = self._safe_path(relative_path)
            except (ValueError, TypeError) as exc:
                errors.append(f"{relative_path}: {exc}")
                continue

            if target.suffix == ".py":
                try:
                    ast.parse(content, filename=str(target))
                    checks.append({
                        "path": relative_path,
                        "check": "python_syntax",
                        "ok": True,
                    })
                except SyntaxError as exc:
                    errors.append(
                        f"{relative_path}: syntax error at line "
                        f"{exc.lineno}: {exc.msg}"
                    )
                    checks.append({
                        "path": relative_path,
                        "check": "python_syntax",
                        "ok": False,
                    })
                    continue

            if target.exists() and not overwrite:
                warnings.append(
                    f"{relative_path}: already exists; not overwritten."
                )
                continue

            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                if overwrite:
                    target.write_text(content, encoding="utf-8")
                else:
                    # Exclusive creation avoids overwriting a file that
                    # appeared after the existence check.
                    with target.open("x", encoding="utf-8") as handle:
                        handle.write(content)
                created.append(relative_path)
            except FileExistsError:
                warnings.append(
                    f"{relative_path}: already exists; not overwritten."
                )
            except OSError as exc:
                errors.append(f"{relative_path}: write failed: {exc}")

        return BuildResult(
            ok=not errors,
            language="mixed",
            files=created,
            checks=checks,
            errors=errors,
            warnings=warnings,
        )

    def python_compile_all(self) -> dict[str, Any]:
        if not self.project_root.is_dir():
            return {
                "ok": False,
                "error": "Project directory does not exist.",
            }

        try:
            ok = compileall.compile_dir(
                str(self.project_root),
                quiet=1,
                force=False,
                maxlevels=20,
                rx=r"[/\\](\.git|\.venv|venv|node_modules|__pycache__)[/\\]",
            )
            return {
                "ok": bool(ok),
                "project_root": str(self.project_root),
                "check": "python_compileall",
            }
        except (OSError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}


__all__ = ["AdvancedCodeBuilder", "BuildResult"]
