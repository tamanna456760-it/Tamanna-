"""Conservative static security checks for Python source (no execution)."""
from __future__ import annotations

import ast
from typing import Any


_RULES = {
    "eval": ("high", "Dynamic eval() can execute untrusted Python expressions."),
    "exec": ("high", "Dynamic exec() can execute arbitrary Python code."),
    "pickle.loads": ("high", "Untrusted pickle data can execute code during deserialization."),
    "yaml.load": ("medium", "Use yaml.safe_load for untrusted YAML input."),
}


class _SecurityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    @staticmethod
    def _call_name(node: ast.AST) -> str:
        parts: list[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))

    def visit_Call(self, node: ast.Call) -> None:
        name = self._call_name(node.func)
        if name in _RULES:
            severity, message = _RULES[name]
            self.findings.append({
                "rule": name,
                "severity": severity,
                "line": node.lineno,
                "message": message,
            })
        if name in {"subprocess.run", "subprocess.Popen", "subprocess.call"}:
            shell_true = any(
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in node.keywords
            )
            if shell_true:
                self.findings.append({
                    "rule": "subprocess.shell_true",
                    "severity": "medium",
                    "line": node.lineno,
                    "message": "shell=True increases command-injection risk; validate arguments and prefer argv lists.",
                })
        self.generic_visit(node)


def scan_python_source(source: str) -> dict[str, Any]:
    """Return syntax status and static findings without running the source."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "valid": False,
            "findings": [{
                "rule": "python.syntax_error",
                "severity": "error",
                "line": exc.lineno or 1,
                "message": exc.msg,
            }],
        }
    visitor = _SecurityVisitor()
    visitor.visit(tree)
    return {"valid": True, "findings": visitor.findings, "count": len(visitor.findings)}


__all__ = ["scan_python_source"]
