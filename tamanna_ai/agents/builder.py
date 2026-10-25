"""Tamanna AI Builder Agent.
Creates new project files without overwriting existing files by default.
"""
from pathlib import Path
from typing import Union
PathLike = Union[str, Path]
class BuilderAgent:
    def __init__(self, project_root: PathLike = "."):
        self.project_root = Path(project_root).resolve()
    def _safe_path(self, relative_path: PathLike) -> Path:
        target = (self.project_root / relative_path).resolve()
        if target != self.project_root and self.project_root not in target.parents:
            raise ValueError("Path is outside the project directory.")
        return target
    def create_file(
        self,
        relative_path: PathLike,
        content: str = "",
        overwrite: bool = False,
    ) -> dict:
        target = self._safe_path(relative_path)
        if target.exists() and not overwrite:
            return {
                "success": False,
                "status": "already_exists",
                "path": str(target),
            }
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive mode prevents accidentally replacing an existing file.
        if not overwrite:
            try:
                with target.open("x", encoding="utf-8") as file:
                    file.write(content)
            except FileExistsError:
                return {
                    "success": False,
                    "status": "already_exists",
                    "path": str(target),
                }
        else:
            target.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "status": "created" if not overwrite else "written",
            "path": str(target),
        }
if __name__ == "__main__":
    agent = BuilderAgent()
    print("Tamanna Builder Agent ready.")