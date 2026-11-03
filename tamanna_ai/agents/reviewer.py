"""Bounded, read-only static review checks for Tamanna AI Python files."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Union


class ReviewerAgent:
    """Inspect Python syntax and selected risky call patterns; never execute code."""

    MAX_SOURCE_BYTES = 1_000_000

    @staticmethod
    def _failure(message: str, path: str | None = None) -> dict:
        result = {
            "passed": False,
            "findings": [{"severity": "high", "message": message}],
            "note": "Static checks only; this is not a complete security audit.",
        }
        if path is not None:
            result["path"] = path
        return result

    def review_python(self, source: str) -> dict:
        """Review bounded Python source without importing or executing it."""
        if not isinstance(source, str):
            return self._failure("Python source must be text.")
        if not source.strip():
            return self._failure("Python source is empty.")
        try:
            source_size = len(source.encode("utf-8"))
        except UnicodeEncodeError:
            return self._failure("Python source must contain valid Unicode text.")
        if source_size > self.MAX_SOURCE_BYTES:
            return self._failure(
                f"Python source exceeds the {self.MAX_SOURCE_BYTES}-byte limit."
            )

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return {
                "passed": False,
                "findings": [{
                    "severity": "high",
                    "message": f"Python syntax error: {exc.msg or 'invalid syntax'}",
                    "line": exc.lineno,
                    "column": exc.offset,
                }],
                "note": "Static checks only; this is not a complete security audit.",
            }
        except (ValueError, TypeError, RecursionError):
            return self._failure("Python source could not be reviewed safely.")

        findings = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else None
            dotted = (
                f"{func.value.id}.{func.attr}"
                if isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                else None
            )

            message = None
            severity = "high"
            if name == "eval":
                message = "Review eval(); it evaluates dynamically supplied expressions."
            elif name == "exec":
                message = "Review exec(); it executes dynamically supplied code."
            elif dotted == "os.system":
                message = "Review os.system(); prefer a constrained subprocess API."
            elif dotted == "subprocess.Popen" or dotted == "subprocess.run":
                if any(keyword.arg == "shell" and isinstance(keyword.value, ast.Constant)
                       and keyword.value.value is True for keyword in node.keywords):
                    message = "Review subprocess shell=True; avoid shell command construction."
            elif dotted == "pickle.loads" or dotted == "pickle.load":
                message = "Review pickle deserialization; untrusted pickle data can execute code."
            elif dotted == "yaml.load":
                message = "Review yaml.load(); use a safe YAML loader for untrusted input."
            elif name == "input":
                severity = "info"
                message = "Check that input() data is validated before use."

            if message:
                findings.append({
                    "severity": severity,
                    "message": message,
                    "line": getattr(node, "lineno", None),
                })

        return {
            "passed": not any(item["severity"] == "high" for item in findings),
            "findings": findings,
            "note": "Static checks only; this is not a complete security audit.",
        }

    def review_file(self, file_path: Union[str, Path]) -> dict:
        """Read and review a bounded UTF-8 .py file without modifying it."""
        if not isinstance(file_path, (str, Path)):
            return self._failure("File path must be text or a Path.")
        path = Path(file_path)
        result_path = str(path)
        if path.suffix.lower() != ".py":
            return self._failure("A Python file is required.", result_path)
        try:
            if not path.is_file():
                return self._failure("Python file was not found.", result_path)
            source_bytes = path.read_bytes()
        except (OSError, ValueError):
            return self._failure("Python file could not be read.", result_path)

        if len(source_bytes) > self.MAX_SOURCE_BYTES:
            return self._failure(
                f"Python file exceeds the {self.MAX_SOURCE_BYTES}-byte limit.",
                result_path,
            )
        try:
            source = source_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return self._failure("Python file must use UTF-8 encoding.", result_path)

        result = self.review_python(source)
        result["path"] = result_path
        return result


if __name__ == "__main__":
    print("Tamanna Reviewer Agent ready.")
