"""Conservative optimization hints; source is never rewritten or executed."""
import ast
from typing import Any

def suggest_optimizations(source: str) -> dict[str, Any]:
    if not isinstance(source, str):
        raise TypeError("source must be text")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"valid": False, "suggestions": [], "error": {"line": exc.lineno or 1, "message": exc.msg}}
    suggestions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
            suggestions.append({"line": node.lineno, "kind": "loop_review", "message": "Check whether repeated work can be reduced or replaced by a built-in operation."})
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"append", "extend"}:
            suggestions.append({"line": node.lineno, "kind": "collection_growth", "message": "For large loops, review allocation and repeated collection growth."})
    return {"valid": True, "suggestions": suggestions, "modified_source": False}

__all__ = ["suggest_optimizations"]
