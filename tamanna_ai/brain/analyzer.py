"""Safe static analysis facade; inspected Python is never executed."""
from __future__ import annotations
import ast
from pathlib import Path
from typing import Any
from tamanna_ai.analysis.complexity import analyze_complexity
from tamanna_ai.analysis.security import scan_python_source

def analyze_source(source: str) -> dict[str, Any]:
    if not isinstance(source, str):
        raise TypeError("source must be text")
    try:
        ast.parse(source)
        syntax_error = None
        complexity = analyze_complexity(source)
    except SyntaxError as exc:
        syntax_error = {"line": exc.lineno or 1, "message": exc.msg}
        complexity = None
    return {"syntax_valid": syntax_error is None, "syntax_error": syntax_error,
            "complexity": complexity, "security": scan_python_source(source)}

def analyze_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    return {"path": str(file_path), **analyze_source(file_path.read_text(encoding="utf-8"))}

__all__ = ["analyze_source", "analyze_file"]
