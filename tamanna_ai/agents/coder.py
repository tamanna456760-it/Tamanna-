"""Tamanna AI Coder Agent."""
import ast
from pathlib import Path
from typing import Union
class CoderAgent:
    def validate_python(self, source: str) -> dict:
        try:
            ast.parse(source)
            return {"valid": True, "error": None}
        except SyntaxError as exc:
            return {
                "valid": False,
                "error": exc.msg,
                "line": exc.lineno,
                "column": exc.offset,
            }
    def validate_file(self, file_path: Union[str, Path]) -> dict:
        path = Path(file_path)
        if not path.is_file():
            return {
                "valid": False,
                "error": "File not found.",
                "path": str(path),
            }
        if path.suffix != ".py":
            return {
                "valid": False,
                "error": "Only Python files are supported.",
                "path": str(path),
            }
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return {
                "valid": False,
                "error": str(exc),
                "path": str(path),
            }
        result = self.validate_python(source)
        result["path"] = str(path)
        return result
if __name__ == "__main__":
    print("Tamanna Coder Agent ready.")