"""Tamanna AI Reviewer Agent."""
import ast
from pathlib import Path
class ReviewerAgent:
    def review_python(self, source: str) -> dict:
        findings = []
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return {
                "passed": False,
                "findings": [{
                    "severity": "high",
                    "message": f"Python syntax error: {exc.msg}",
                    "line": exc.lineno,
                }],
            }
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "eval":
                    findings.append({
                        "severity": "high",
                        "message": "Review eval() carefully; it can execute untrusted code.",
                        "line": node.lineno,
                    })
                if isinstance(func, ast.Name) and func.id == "exec":
                    findings.append({
                        "severity": "high",
                        "message": "Review exec() carefully; it can execute dynamic code.",
                        "line": node.lineno,
                    })
                if isinstance(func, ast.Name) and func.id == "input":
                    findings.append({
                        "severity": "info",
                        "message": "Check that user input is validated.",
                        "line": node.lineno,
                    })
        return {
            "passed": not any(
                item["severity"] == "high" for item in findings
            ),
            "findings": findings,
            "note": "Static checks only; this is not a complete security audit.",
        }
    def review_file(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.is_file() or path.suffix != ".py":
            return {
                "passed": False,
                "findings": [{
                    "severity": "high",
                    "message": "A readable Python file is required.",
                }],
            }
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return {
                "passed": False,
                "findings": [{
                    "severity": "high",
                    "message": str(exc),
                }],
            }
        result = self.review_python(source)
        result["path"] = str(path)
        return result
if __name__ == "__main__":
    print("Tamanna Reviewer Agent ready.")