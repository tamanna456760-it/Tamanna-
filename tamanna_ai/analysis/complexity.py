"""Dependency-free Python source complexity metrics."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class _ComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: list[dict[str, Any]] = []
        self.classes = 0
        self.imports = 0
        self.decisions = 0
        self._current: dict[str, Any] | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.imports += len(node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports += len(node.names)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        previous = self._current
        current = {"name": node.name, "line": node.lineno, "complexity": 1}
        self._current = current
        for child in node.body:
            self.visit(child)
        self.functions.append(current)
        self._current = previous

    def _decision(self) -> None:
        self.decisions += 1
        if self._current is not None:
            self._current["complexity"] += 1

    def visit_If(self, node: ast.If) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._decision()
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self._decision()
        if self._current is not None:
            self._current["complexity"] += max(0, len(node.values) - 2)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._decision()
        if self._current is not None:
            self._current["complexity"] += max(0, len(node.cases) - 1)
        self.generic_visit(node)


def analyze_complexity(source: str) -> dict[str, Any]:
    """Analyze Python source text; no code is executed."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    tree = ast.parse(source)
    visitor = _ComplexityVisitor()
    visitor.visit(tree)
    return {
        "lines": len(source.splitlines()),
        "functions": len(visitor.functions),
        "classes": visitor.classes,
        "imports": visitor.imports,
        "decision_points": visitor.decisions,
        "cyclomatic_complexity": sum(item["complexity"] for item in visitor.functions),
        "functions_detail": sorted(visitor.functions, key=lambda item: item["line"]),
    }


def analyze_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    return {"path": str(file_path), **analyze_complexity(file_path.read_text(encoding="utf-8"))}


calculate_complexity = analyze_complexity

__all__ = ["analyze_complexity", "calculate_complexity", "analyze_file"]
