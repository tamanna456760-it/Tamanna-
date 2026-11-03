"""Safe, local file operations for the Tamanna AI code builder."""

from __future__ import annotations

import ast
import os
import stat
import tempfile
from pathlib import Path
from typing import Any


class IntelligentCodeBuilder:
    """Inspect and update text files inside a single project directory.

    Writes are deliberately limited to confirmed requests, validated paths,
    bounded text payloads, and atomic replacements.
    """

    MAX_CONTENT_BYTES = 1_000_000
    EXCLUDED_DIRS = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
    }
    BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ValueError("Project root must be an existing directory.")

    def _resolve_path(self, relative_path: str | Path) -> Path:
        raw = str(relative_path)
        if not raw or "\x00" in raw:
            raise ValueError("A valid relative file path is required.")

        candidate = Path(raw)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError("Absolute paths and parent traversal are not allowed.")

        if any(part in self.EXCLUDED_DIRS for part in candidate.parts):
            raise ValueError("This project path is protected.")

        if candidate.name == ".env" or candidate.name.startswith(".env."):
            raise ValueError("Environment files are protected.")

        if candidate.suffix.lower() in self.BLOCKED_SUFFIXES:
            raise ValueError("Private key and certificate files are protected.")

        target = (self.project_root / candidate).resolve()
        try:
            target.relative_to(self.project_root)
        except ValueError as exc:
            raise ValueError("Path resolves outside the project directory.") from exc

        if target == self.project_root:
            raise ValueError("A file path is required.")
        return target

    @staticmethod
    def _validate_python(path: Path, content: str) -> None:
        if path.suffix.lower() == ".py":
            try:
                ast.parse(content, filename=str(path))
            except SyntaxError as exc:
                raise ValueError(
                    f"Python syntax error on line {exc.lineno}: {exc.msg}"
                ) from exc

    def scan_project(self) -> dict[str, Any]:
        files = []
        errors = []

        for current, directories, filenames in os.walk(
            self.project_root, followlinks=False
        ):
            directories[:] = sorted(
                name for name in directories
                if name not in self.EXCLUDED_DIRS
            )
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                path = Path(current) / filename
                try:
                    path.resolve().relative_to(self.project_root)
                    source = path.read_text(encoding="utf-8")
                    ast.parse(source, filename=str(path))
                except SyntaxError as exc:
                    errors.append({
                        "path": str(path.relative_to(self.project_root)),
                        "line": exc.lineno,
                        "error": exc.msg,
                    })
                except (OSError, UnicodeError, ValueError) as exc:
                    errors.append({
                        "path": str(path.relative_to(self.project_root)),
                        "error": type(exc).__name__,
                    })
                files.append(str(path.relative_to(self.project_root)))

        return {
            "status": "ok" if not errors else "issues_found",
            "root": str(self.project_root),
            "total_files": len(files),
            "python_files": len(files),
            "syntax_errors": len(errors),
            "errors": errors[:200],
            "truncated_errors": len(errors) > 200,
        }

    def inspect(self, relative_path: str) -> dict[str, Any]:
        target = self._resolve_path(relative_path)
        if not target.is_file():
            return {
                "status": "not_found",
                "path": relative_path,
                "exists": False,
            }

        try:
            source = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return {
                "status": "error",
                "path": relative_path,
                "error": type(exc).__name__,
            }

        return {
            "status": "ok",
            "path": str(target.relative_to(self.project_root)),
            "exists": True,
            "type": "python" if target.suffix.lower() == ".py" else "text",
            "lines": len(source.splitlines()),
            "size_bytes": target.stat().st_size,
        }

    def propose_write(self, relative_path: str, content: str) -> dict[str, Any]:
        target = self._resolve_path(relative_path)
        if not isinstance(content, str):
            raise ValueError("File content must be text.")

        size = len(content.encode("utf-8"))
        if size > self.MAX_CONTENT_BYTES:
            raise ValueError("File content exceeds the 1 MB limit.")
        self._validate_python(target, content)

        return {
            "status": "ok",
            "mode": "preview",
            "path": str(target.relative_to(self.project_root)),
            "content_length": size,
            "preview": content[:250],
            "requires_confirmation": True,
        }

    def apply_write(
        self, relative_path: str, content: str, confirm: bool = False
    ) -> dict[str, Any]:
        if confirm is not True:
            return {
                "status": "confirmation_required",
                "path": relative_path,
                "applied": False,
            }

        target = self._resolve_path(relative_path)
        if not isinstance(content, str):
            raise ValueError("File content must be text.")

        encoded = content.encode("utf-8")
        if len(encoded) > self.MAX_CONTENT_BYTES:
            raise ValueError("File content exceeds the 1 MB limit.")
        self._validate_python(target, content)

        target.parent.mkdir(parents=True, exist_ok=True)
        # Re-resolve after directory creation to reject a symlinked parent.
        target = self._resolve_path(relative_path)
        old_mode = (
            stat.S_IMODE(target.stat().st_mode)
            if target.exists() and target.is_file()
            else 0o644
        )

        fd, temporary_name = tempfile.mkstemp(
            prefix=".tamanna-write-", suffix=".tmp", dir=str(target.parent)
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(encoded)
                output.flush()
                os.fsync(output.fileno())
            os.chmod(temporary, old_mode)
            os.replace(temporary, target)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

        return {
            "status": "ok",
            "path": str(target.relative_to(self.project_root)),
            "applied": True,
            "bytes_written": len(encoded),
        }


__all__ = ["IntelligentCodeBuilder"]
