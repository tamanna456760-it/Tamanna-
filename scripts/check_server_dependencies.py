#!/usr/bin/env python3
"""Check third-party imports in Main.py and its mandatory Tamanna package import closure."""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = {
    "tamanna_ai.persistence.database",
    "tamanna_ai.integrations.provider",
    "tamanna_ai.tools.safe_tools",
    "tamanna_ai.authentication.router",
    "tamanna_ai.authentication.access_control",
    "tamanna_ai.core.controller",
    "tamanna_ai.skills",
    "tamanna_ai.code_builder",
}
STDLIB = set(sys.stdlib_module_names)
queue = ["Main"] + sorted(SEEDS)
visited: set[str] = set()
external: set[str] = set()
failures: list[str] = []


def module_path(name: str) -> Path | None:
    parts = name.split(".")
    candidate = ROOT.joinpath(*parts).with_suffix(".py")
    if candidate.is_file():
        return candidate
    package = ROOT.joinpath(*parts, "__init__.py")
    if package.is_file():
        return package
    return None


def is_local(name: str) -> bool:
    top = name.split(".", 1)[0]
    return (ROOT / (top + ".py")).is_file() or (ROOT / top / "__init__.py").is_file()


def imports_from(path: Path, module_name: str) -> tuple[set[str], set[str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        failures.append(f"Cannot parse {path.relative_to(ROOT)}: {exc}")
        return set(), set()
    required: set[str] = set()
    internal: set[str] = set()

    class Visitor(ast.NodeVisitor):
        optional_depth = 0

        def visit_Try(self, node: ast.Try) -> None:
            optional = any(
                handler.type is None
                or (isinstance(handler.type, ast.Name) and handler.type.id in {"ImportError", "ModuleNotFoundError", "Exception"})
                for handler in node.handlers
            )
            if optional:
                self.optional_depth += 1
            for child in node.body:
                self.visit(child)
            if optional:
                self.optional_depth -= 1
            for child in node.handlers + node.orelse + node.finalbody:
                self.visit(child)

        def _record(self, name: str) -> None:
            if self.optional_depth:
                return
            if name.startswith("tamanna_ai"):
                internal.add(name)
            else:
                top = name.split(".", 1)[0]
                if top not in STDLIB and not is_local(name):
                    required.add(top)

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                self._record(alias.name)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.level:
                base = module_name.split(".")[:-node.level]
                target = ".".join(base + ([node.module] if node.module else []))
            else:
                target = node.module or ""
            if target:
                self._record(target)

    Visitor().visit(tree)
    return required, internal


main_path = ROOT / "Main.py"
if not main_path.is_file():
    failures.append("Main.py is missing")
else:
    external_names, internal_names = imports_from(main_path, "Main")
    external.update(external_names)
    queue.extend(sorted(internal_names))

while queue:
    module = queue.pop()
    if module in visited:
        continue
    visited.add(module)
    path = module_path(module)
    if path is None:
        failures.append(f"Required internal module is missing: {module}")
        continue
    required, internal = imports_from(path, module)
    external.update(required)
    queue.extend(sorted(internal - visited))

missing = []
for name in sorted(external):
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ModuleNotFoundError, ValueError):
        spec = None
    if spec is None:
        missing.append(name)

print("Server import-closure modules checked:")
for name in sorted(visited):
    print(f"  {name}")
print("Third-party imports checked:")
for name in sorted(external):
    print(f"  {name}")
if missing or failures:
    for name in missing:
        print(f"MISSING DISTRIBUTION IMPORT: {name}")
    for failure in failures:
        print(f"FAIL: {failure}")
    raise SystemExit(1)
print("PASS: all mandatory server import dependencies are available.")
