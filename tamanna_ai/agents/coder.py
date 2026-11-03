"""Read-only Python validation utilities for Tamanna AI."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Union


class CoderAgent:
    """Validate Python source without executing or modifying it."""

    MAX_SOURCE_BYTES = 1_000_000

    @staticmethod
    def _failure(message: str, **details) -> dict:
        return {"valid": False, "error": message, **details}

    def validate_python(self, source: str) -> dict:
        """Parse source safely and report syntax diagnostics without execution."""
        if not isinstance(source, str):
            return self._failure("Python source must be text.")
        if not source.strip():
            return self._failure("Python source is empty.")
        if len(source.encode("utf-8")) > self.MAX_SOURCE_BYTES:
            return self._failure(
                f"Python source exceeds the {self.MAX_SOURCE_BYTES}-byte limit."
            )
        try:
            ast.parse(source)
            return {"valid": True, "error": None, "line": None, "column": None}
        except SyntaxError as exc:
            return self._failure(
                exc.msg or "Invalid Python syntax.",
                line=exc.lineno,
                column=exc.offset,
            )
        except (ValueError, TypeError, RecursionError):
            return self._failure("Python source could not be parsed safely.")

    def validate_file(self, file_path: Union[str, Path]) -> dict:
        """Read and validate a bounded .py file; never execute or write it."""
        if not isinstance(file_path, (str, Path)):
            return self._failure("File path must be text or a Path.")
        path = Path(file_path)
        result_path = str(path)
        if path.suffix.lower() != ".py":
            return self._failure("Only Python files are supported.", path=result_path)
        try:
            if not path.is_file():
                return self._failure("Python file was not found.", path=result_path)
            source_bytes = path.read_bytes()
        except (OSError, ValueError):
            return self._failure("Python file could not be read.", path=result_path)

        if len(source_bytes) > self.MAX_SOURCE_BYTES:
            return self._failure(
                f"Python file exceeds the {self.MAX_SOURCE_BYTES}-byte limit.",
                path=result_path,
            )
        try:
            source = source_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return self._failure("Python file must use UTF-8 encoding.", path=result_path)

        result = self.validate_python(source)
        result["path"] = result_path
        return result


if __name__ == "__main__":
    print("Tamanna Coder Agent ready.")
