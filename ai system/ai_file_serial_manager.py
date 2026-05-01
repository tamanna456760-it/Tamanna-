#!/usr/bin/env python3
"""
Advanced File Serial Renamer

Recursively or non‑recursively rename files with a sequential number.
Features: custom prefix, start number, extension filter, dry‑run, safe overwrite handling.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# ------------------------------------------------------------
# Natural sorting (so "file2" comes before "file10")
# ------------------------------------------------------------
def natural_sort_key(path: Path) -> List:
    """Split path stem into text and numbers for human‑like sorting."""
    import re
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    parts = re.split(r'(\d+)', path.stem)
    return [convert(p) for p in parts]

# ------------------------------------------------------------
# Main renaming logic
# ------------------------------------------------------------
def serial_rename(
    folder: Path,
    prefix: str = "File",
    start: int = 1,
    dry_run: bool = False,
    recursive: bool = False,
    extensions: Optional[List[str]] = None,
) -> None:
    """
    Rename files in `folder` to `prefix_XXX.ext` (with safe duplicate handling).

    Args:
        folder: directory to process
        prefix: name prefix for new files
        start: starting number (e.g. 1 -> 001)
        dry_run: if True, only show what would be done
        recursive: process subfolders as well
        extensions: list of extensions to include (e.g. ['.txt', '.jpg'])
    """
    if not folder.exists():
        print(f"❌ Folder does not exist: {folder}")
        return

    # Collect all files (or recursively)
    if recursive:
        all_files = [p for p in folder.rglob("*") if p.is_file()]
    else:
        all_files = [p for p in folder.iterdir() if p.is_file()]

    # Filter by extension if requested
    if extensions:
        # Normalise extensions: user may give '.txt' or 'txt'
        ext_set = {e if e.startswith('.') else f'.{e}' for e in extensions}
        all_files = [p for p in all_files if p.suffix.lower() in ext_set]

    # Sort naturally (e.g. 'img10' after 'img2')
    all_files.sort(key=natural_sort_key)

    count = start
    renamed_count = 0
    skipped_count = 0

    for file_path in all_files:
        ext = file_path.suffix
        new_name = f"{prefix}_{count:03d}{ext}"
        new_path = file_path.parent / new_name

        # Safety: if new name already exists, find an unused name
        final_path = new_path
        dup_num = 1
        while final_path.exists() and final_path != file_path:
            final_path = file_path.parent / f"{prefix}_{count:03d}_dup{dup_num}{ext}"
            dup_num += 1

        # If the file would stay the same, skip
        if final_path == file_path:
            print(f"⏭️  Skipped  : {file_path.name} (already has target name)")
            skipped_count += 1
            count += 1
            continue

        # Perform rename (or dry run)
        action = "Would rename" if dry_run else "Renamed"
        print(f"{action}: {file_path.name} -> {final_path.name}")

        if not dry_run:
            try:
                file_path.rename(final_path)
                renamed_count += 1
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                skipped_count += 1
        else:
            renamed_count += 1

        count += 1

    # Summary
    print("\n" + "=" * 50)
    if dry_run:
        print(f"🔍 DRY RUN – would rename {renamed_count} file(s), skip {skipped_count}.")
    else:
        print(f"✅ Done – renamed {renamed_count} file(s), skipped {skipped_count}.")
    print("=" * 50)

# ------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Serially rename files with a custom prefix and number.",
        epilog="Example: python rename.py ./docs --prefix Doc --start 5 --dry-run"
    )
    parser.add_argument(
        "folder", nargs="?", default="./files",
        help="Folder containing files to rename (default: ./files)"
    )
    parser.add_argument(
        "--prefix", "-p", default="File",
        help="Prefix for new filenames (default: File)"
    )
    parser.add_argument(
        "--start", "-s", type=int, default=1,
        help="Starting number (default: 1)"
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true",
        help="Preview changes without renaming"
    )
    parser.add_argument(
        "--recursive", "-r", action="store_true",
        help="Process subfolders recursively"
    )
    parser.add_argument(
        "--extensions", "-e", nargs="+",
        help="Only rename files with these extensions (e.g. -e .txt .jpg)"
    )
    parser.add_argument(
        "--create", "-c", action="store_true",
        help="Create the target folder if it does not exist"
    )

    args = parser.parse_args()

    folder = Path(args.folder)

    # Optionally create folder
    if args.create and not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created folder: {folder}")

    # Run the renamer
    serial_rename(
        folder=folder,
        prefix=args.prefix,
        start=args.start,
        dry_run=args.dry_run,
        recursive=args.recursive,
        extensions=args.extensions,
    )

if __name__ == "__main__":
    main()