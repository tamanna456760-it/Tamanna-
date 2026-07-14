#!/usr/bin/env python3
"""
Project Structure Synchronizer & Monitor
-----------------------------------------
- Reads a folder tree from 'project_tree.txt'
- Creates all missing directories and files with sensible defaults
- Monitors the filesystem and recreates missing files on the fly
- Ensures the project stays exactly as defined
"""

import os
import sys
import re
import time
import json
import shutil
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Default templates for different file types
# ----------------------------------------------------------------------
TEMPLATES = {
    ".py": '''#!/usr/bin/env python3
"""
{filename} - Auto-generated module
"""

def main():
    print("{filename} is running")

if __name__ == "__main__":
    main()
''',
    ".js": """// {filename}
console.log("{filename} loaded");

module.exports = {{}};
""",
    ".json": {{}},
    ".html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>Auto-generated file: {filename}</p>
</body>
</html>
""",
    ".css": """/* {filename} */
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}}
""",
    ".sh": """#!/bin/bash
# {filename}
echo "Running {filename}"
""",
    ".yaml": "# {filename}\n",
    ".yml": "# {filename}\n",
    ".txt": "Auto-generated file: {filename}\n",
    ".md": "# {filename}\n\nAuto-generated documentation.\n",
    ".sql": "-- {filename}\n",
    ".xml": "<!-- {filename} -->\n<root/>\n",
    ".kotlin": """// {filename}
fun main() {{
    println("{filename} is running")
}}
""",
    ".java": """// {filename}
public class {classname} {{
    public static void main(String[] args) {{
        System.out.println("{filename} is running");
    }}
}}
""",
}


def get_template(filepath):
    """Return appropriate content for a missing file based on its extension."""
    ext = Path(filepath).suffix.lower()
    name = Path(filepath).name
    title = name.replace("_", " ").replace(".", " ").title()
    classname = Path(filepath).stem.replace("-", "_").replace(".", "_")

    if ext in TEMPLATES:
        template = TEMPLATES[ext]
        if isinstance(template, dict):
            return json.dumps({}, indent=2)  # empty JSON
        elif ext == ".html":
            return template.format(filename=name, title=title)
        elif ext == ".java":
            return template.format(filename=name, classname=classname)
        else:
            return template.format(filename=name)
    else:
        # Fallback: empty file with a comment line
        return f"# Auto-generated: {name}\n"


# ----------------------------------------------------------------------
# 2. Parse tree from text file (supports typical 'tree' output)
# ----------------------------------------------------------------------
def parse_tree_file(tree_path):
    """
    Reads a file containing a folder tree (like output of `tree` command)
    and returns a set of relative file paths that should exist.
    """
    if not os.path.isfile(tree_path):
        print(f"ERROR: Tree file '{tree_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(tree_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove any leading/trailing empty lines
    lines = [line.rstrip("\n") for line in lines if line.strip()]

    # We'll maintain a stack of current directory levels (based on indentation)
    # and a set of resulting absolute paths relative to root.
    rel_paths = set()
    # Stack entries: (indent_level, current_path)
    stack = [(0, "")]
    indent_chars = "│ └─├─📁 "  # characters used in tree lines

    for line in lines:
        # Strip leading box-drawing characters but keep the indentation level
        stripped = line.lstrip("│ └─├─📁 ")
        # Count how many leading spaces? Actually easier: detect prefix length
        # Find the first non-space, non-special character position
        match = re.match(r"^[│ └─├─📁]*", line)
        if match:
            prefix_len = len(match.group(0))
        else:
            prefix_len = 0

        # Determine indentation level (roughly every 2 or 4 spaces)
        # For simplicity, we consider each "segment" as 2 characters (e.g., "├─" or "└─")
        level = prefix_len // 2

        # Remove the prefix and any extra spaces
        name = line[prefix_len:].strip()
        if not name:
            continue

        # Remove emoji folder icon if present
        name = re.sub(r"📁", "", name).strip()

        # Adjust stack to match current level
        while stack and stack[-1][0] >= level:
            stack.pop()

        parent_path = stack[-1][1] if stack else ""
        current_path = os.path.join(parent_path, name) if parent_path else name

        # Determine if it's a file or folder
        # In tree listings, folders often end with '/', but not always.
        # Heuristic: if the line contains "├─" or "└─" and no extension, it's a folder.
        # Also, if we see a '.' in the last part, treat as file.
        if "." in name and not name.endswith("/"):
            # It's a file
            rel_paths.add(current_path)
        else:
            # It's a folder – push to stack
            stack.append((level, current_path))

    return rel_paths


# ----------------------------------------------------------------------
# 3. Synchronize filesystem with the parsed structure
# ----------------------------------------------------------------------
def sync_structure(root_dir, expected_paths):
    """
    Create all directories and files from expected_paths.
    For missing files, write a default template.
    """
    root = Path(root_dir).resolve()
    created = 0
    for rel_path in expected_paths:
        full_path = root / rel_path
        if full_path.is_dir():
            continue  # we only create files; folders are created by parent

        # Ensure parent directory exists
        parent = full_path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
            print(f"[CREATED] Directory: {parent}")

        if not full_path.exists():
            # Write default content
            content = get_template(full_path)
            try:
                if isinstance(content, dict):
                    with open(full_path, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=2)
                else:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                # Make .sh and .py files executable on Unix
                if full_path.suffix in (".sh", ".py"):
                    full_path.chmod(0o755)
                print(f"[CREATED] File: {full_path}")
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {full_path}: {e}")

    print(f"\n✅ Synchronization complete. {created} files created.")
    return created


# ----------------------------------------------------------------------
# 4. Monitoring (optional, using watchdog if available)
# ----------------------------------------------------------------------
def start_monitoring(root_dir, expected_paths, interval=10):
    """
    Periodically check that all expected files exist.
    If a file is missing, recreate it.
    (This is a simple polling monitor; you can replace with watchdog.)
    """
    root = Path(root_dir).resolve()
    print(f"\n🔍 Starting monitor (polling every {interval}s)... Press Ctrl+C to stop.")
    try:
        while True:
            for rel_path in expected_paths:
                full_path = root / rel_path
                if not full_path.exists():
                    print(f"[MISSING] {full_path} – recreating...")
                    parent = full_path.parent
                    parent.mkdir(parents=True, exist_ok=True)
                    content = get_template(full_path)
                    if isinstance(content, dict):
                        with open(full_path, "w", encoding="utf-8") as f:
                            json.dump(content, f, indent=2)
                    else:
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                    if full_path.suffix in (".sh", ".py"):
                        full_path.chmod(0o755)
                    print(f"[RECREATED] {full_path}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")


# ----------------------------------------------------------------------
# 5. Main entry point
# ----------------------------------------------------------------------
def main():
    # Configuration
    TREE_FILE = "project_tree.txt"  # file containing the tree output
    PROJECT_ROOT = "."  # current directory (change if needed)

    print("🔧 Project Structure Synchronizer & Monitor")
    print("============================================")

    # Step 1: Parse tree file
    print(f"\n📖 Reading tree from '{TREE_FILE}' ...")
    expected = parse_tree_file(TREE_FILE)
    if not expected:
        print("ERROR: No files found in tree. Check your project_tree.txt format.")
        sys.exit(1)
    print(f"   Found {len(expected)} files in the tree.")

    # Step 2: Create missing files/folders
    sync_structure(PROJECT_ROOT, expected)

    # Step 3: Ask if user wants to monitor
    print("\n" + "=" * 50)
    answer = (
        input(
            "Do you want to continuously monitor the project and auto-fix missing files? (y/n): "
        )
        .strip()
        .lower()
    )
    if answer == "y":
        try:
            interval = int(input("Polling interval in seconds (default 10): ") or "10")
        except:
            interval = 10
        start_monitoring(PROJECT_ROOT, expected, interval)
    else:
        print("✅ Setup complete. You can now run your project normally.")
        print(
            "   (If any file is deleted later, run this script again or enable monitoring.)"
        )


if __name__ == "__main__":
    main()
