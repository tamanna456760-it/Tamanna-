"""Small allow-listed tools. No shell, eval, filesystem writes, or arbitrary URLs."""

from __future__ import annotations

import ast
import operator
from typing import Any

_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression: str) -> int | float:
    """Evaluate a bounded arithmetic expression without Python eval()."""
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 200:
        raise ValueError("Provide a non-empty arithmetic expression of at most 200 characters")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid arithmetic expression") from exc

    def visit(node: ast.AST, depth: int = 0) -> int | float:
        if depth > 20:
            raise ValueError("Expression is too complex")
        if isinstance(node, ast.Expression):
            return visit(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**12:
                raise ValueError("Number is out of allowed range")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Exponent is too large")
            result = _BINOPS[type(node.op)](left, right)
            if abs(result) > 10**15:
                raise ValueError("Result is out of allowed range")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
            return _UNARYOPS[type(node.op)](visit(node.operand, depth + 1))
        raise ValueError("Only basic arithmetic is allowed")

    try:
        return visit(tree)
    except ZeroDivisionError as exc:
        raise ValueError("Division by zero") from exc


def run_safe_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run a named built-in tool from the explicit allow-list."""
    if name == "calculator":
        if set(arguments) != {"expression"}:
            raise ValueError("calculator requires only the expression argument")
        return {"tool": name, "result": calculate(str(arguments["expression"]))}
    if name == "project_search":
        if not set(arguments).issubset({"query", "limit"}) or not isinstance(arguments.get("query"), str):
            raise ValueError("project_search requires query and optional limit")
        limit = int(arguments.get("limit", 10))
        if not 1 <= limit <= 20:
            raise ValueError("project_search limit must be between 1 and 20")
        from tamanna_ai.knowledge.resource_search import search_code
        return {"tool": name, "results": search_code(arguments["query"], limit=limit)}
    raise ValueError(f"Tool is not allow-listed: {name}")
