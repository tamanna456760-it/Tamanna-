"""Tamanna AI Tester Agent."""
import ast
import subprocess
import sys
from pathlib import Path
from typing import Optional
class TesterAgent:
    def validate_syntax(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.is_file() or path.suffix != ".py":
            return {
                "success": False,
                "error": "A valid Python file is required.",
            }
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
            return {"success": True, "message": "Syntax check passed."}
        except SyntaxError as exc:
            return {
                "success": False,
                "error": exc.msg,
                "line": exc.lineno,
            }
        except (OSError, UnicodeError) as exc:
            return {"success": False, "error": str(exc)}
    def run_unittest(
        self,
        project_root: str = ".",
        test_path: Optional[str] = None,
        timeout: int = 60,
    ) -> dict:
        root = Path(project_root).resolve()
        if not root.is_dir():
            return {"success": False, "error": "Project directory not found."}
        if not 1 <= timeout <= 300:
            return {"success": False, "error": "Timeout must be 1–300 seconds."}
        target = Path(test_path) if test_path else None
        if target is not None:
            target = (root / target).resolve()
            if root not in target.parents and target != root:
                return {"success": False, "error": "Test path is outside the project."}
            if not target.exists():
                return {"success": False, "error": "Test path not found."}
        command = [sys.executable, "-m", "unittest"]
        if target is None:
            command.append("discover")
        else:
            command.extend(["discover", "-s", str(target)])
        try:
            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[-12000:],
                "stderr": result.stderr[-12000:],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Tests timed out."}
        except OSError as exc:
            return {"success": False, "error": str(exc)}
if __name__ == "__main__":
    print("Tamanna Tester Agent ready.")