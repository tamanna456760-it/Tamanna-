"""Static checks for legacy examples: valid syntax and no import-time execution."""
import ast
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "runner" / "python" / "examples"


def test_legacy_examples_parse_without_execution():
    for path in EXAMPLES.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_legacy_examples_guard_executable_demo_code():
    for path in EXAMPLES.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert any(
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            for node in tree.body
        ), f"{path.name} should guard executable demo code"
