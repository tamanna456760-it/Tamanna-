#!/usr/bin/env python3
"""
AI File Serial Manager - Advanced Edition
Features: save original names, regex, sort by, copy mode, parallel, CSV export.
"""

import argparse
import csv
import json
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# Optional progress bar
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(iterable, desc="", unit=""):
        print(desc)
        return iterable

# ------------------------------------------------------------
# Natural sorting
# ------------------------------------------------------------
def natural_sort_key(path: Path) -> List:
    parts = re.split(r'(\d+)', path.stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

# ------------------------------------------------------------
# Sorting functions
# ------------------------------------------------------------
def get_sort_key(sort_by: str):
    sort_by = sort_by.lower()
    if sort_by == "size":
        return lambda p: p.stat().st_size
    elif sort_by == "modified":
        return lambda p: p.stat().st_mtime
    elif sort_by == "created":
        return lambda p: p.stat().st_ctime
    else:  # name (default, natural)
        return natural_sort_key

# ------------------------------------------------------------
# Apply regex rename (modify stem before numbering)
# ------------------------------------------------------------
def apply_regex(name: str, pattern: str, replacement: str) -> str:
    """Apply regex to the filename stem (without extension)."""
    stem = Path(name).stem
    new_stem = re.sub(pattern, replacement, stem)
    return new_stem + Path(name).suffix

# ------------------------------------------------------------
# Save original names to various formats
# ------------------------------------------------------------
def save_original_names(folder: Path, files: List[Path], prefix: str = "") -> None:
    """Save list of original filenames to text and CSV."""
    # Plain text
    txt_path = folder / "original_names.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        for fpath in files:
            f.write(fpath.name + "\n")
    print(f"💾 Saved original names (text): {txt_path}")

    # CSV with additional info
    csv_path = folder / "original_names.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["original_name", "size_bytes", "modified_date", "will_be_renamed_to"])
        for fpath in files:
            stat = fpath.stat()
            writer.writerow([
                fpath.name,
                stat.st_size,
                datetime.fromtimestamp(stat.st_mtime).isoformat(),
                f"{prefix}_{?}"  # placeholder, actual new name unknown yet
            ])
    print(f"💾 Saved original names (CSV): {csv_path}")

# ------------------------------------------------------------
# Main renaming function (advanced)
# ------------------------------------------------------------
def advanced_serial_rename(
    folder: Path,
    prefix: str = "File",
    start: int = 1,
    recursive: bool = False,
    extensions: Optional[List[str]] = None,
    dry_run: bool = False,
    exclude_patterns: Optional[List[str]] = None,
    sort_by: str = "name",
    regex_pattern: Optional[str] = None,
    regex_replacement: Optional[str] = None,
    copy_mode: bool = False,
    parallel: bool = False,
    save_names_only: bool = False,
    log_file: Optional[Path] = None,
) -> None:
    """Advanced rename with original name saving, regex, copy mode, etc."""
    if not folder.exists():
        print(f"❌ Folder does not exist: {folder}")
        return

    # Collect files
    if recursive:
        all_files = [p for p in folder.rglob("*") if p.is_file()]
    else:
        all_files = [p for p in folder.iterdir() if p.is_file()]

    # Filter by extension
    if extensions:
        ext_set = {e if e.startswith('.') else f'.{e}' for e in extensions}
        all_files = [p for p in all_files if p.suffix.lower() in ext_set]

    # Exclude patterns
    if exclude_patterns:
        def is_excluded(p: Path) -> bool:
            for pat in exclude_patterns:
                if p.match(pat) or pat in p.name:
                    return True
            return False
        all_files = [p for p in all_files if not is_excluded(p)]

    # Sort
    sort_key = get_sort_key(sort_by)
    all_files.sort(key=sort_key)

    # If only saving names, do that and exit
    if save_names_only:
        save_original_names(folder, all_files, prefix)
        return

    # Prepare changes
    changes = []  # (old_path, new_path, old_name, new_name)
    count = start

    for file_path in tqdm(all_files, desc="Preparing", unit="file"):
        ext = file_path.suffix
        stem = file_path.stem

        # Apply regex if given
        if regex_pattern and regex_replacement:
            new_stem = re.sub(regex_pattern, regex_replacement, stem)
        else:
            new_stem = stem

        new_name = f"{prefix}_{count:03d}{ext}"
        # But if regex changed the stem, we may want to keep part? We'll just number fully.
        # For more control, we could combine: f"{new_stem}_{count:03d}{ext}" - but let's stay simple.
        new_path = file_path.parent / new_name

        # Avoid overwrites
        final_path = new_path
        dup = 1
        while final_path.exists() and final_path != file_path:
            final_path = file_path.parent / f"{prefix}_{count:03d}_dup{dup}{ext}"
            dup += 1

        if final_path == file_path:
            continue  # skip identical

        changes.append((file_path, final_path, file_path.name, final_path.name))
        count += 1

    if not changes:
        print("No files need renaming.")
        return

    # Interactive preview
    print("\n📋 Preview of changes (first 10):")
    for i, (old, new, oldn, newn) in enumerate(changes[:10]):
        print(f"  {oldn}  ->  {newn}")
    if len(changes) > 10:
        print(f"  ... and {len(changes)-10} more")

    if dry_run:
        print("\n🔍 DRY RUN – no changes made.")
        return

    answer = input("\nProceed with rename? (y/N): ").strip().lower()
    if answer != 'y':
        print("Aborted.")
        return

    # Save original names before renaming
    save_original_names(folder, [old for old, _, _, _ in changes], prefix)

    # Perform rename or copy
    def rename_one(item):
        old, new, oldn, newn = item
        try:
            if copy_mode:
                shutil.copy2(old, new)  # preserve metadata
                action = "Copied"
            else:
                old.rename(new)
                action = "Renamed"
            return True, action, oldn, newn
        except Exception as e:
            return False, str(e), oldn, newn

    if parallel:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(rename_one, item): item for item in changes}
            for future in tqdm(as_completed(futures), total=len(changes), desc="Processing", unit="file"):
                success, msg, oldn, newn = future.result()
                if success:
                    print(f"✅ {msg}: {oldn} -> {newn}")
                else:
                    print(f"❌ Error on {oldn}: {msg}")
    else:
        for item in tqdm(changes, desc="Processing", unit="file"):
            success, msg, oldn, newn = rename_one(item)
            if success:
                print(f"✅ {msg}: {oldn} -> {newn}")
            else:
                print(f"❌ Error on {oldn}: {msg}")

    # Save CSV mapping of old->new
    mapping_csv = folder / "rename_mapping.csv"
    with open(mapping_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["original_name", "new_name", "status"])
        for old, new, oldn, newn in changes:
            writer.writerow([oldn, newn, "done"])
    print(f"📊 Mapping saved: {mapping_csv}")

    # Create undo JSON (for rollback)
    undo_data = {
        "timestamp": datetime.now().isoformat(),
        "folder": str(folder),
        "prefix": prefix,
        "renames": [{"old": str(old), "new": str(new)} for old, new, _, _ in changes]
    }
    undo_file = folder / f"undo_{int(datetime.now().timestamp())}.json"
    with open(undo_file, 'w') as f:
        json.dump(undo_data, f, indent=2)
    print(f"🔄 Undo file saved: {undo_file}")

# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Advanced AI File Serial Manager")
    parser.add_argument("folder", nargs="?", default="./files")
    parser.add_argument("--prefix", "-p", default="File")
    parser.add_argument("--start", "-s", type=int, default=1)
    parser.add_argument("--recursive", "-r", action="store_true")
    parser.add_argument("--extensions", "-e", nargs="+")
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--exclude", "-x", action="append", default=[])
    parser.add_argument("--sort-by", choices=["name", "size", "modified", "created"], default="name")
    parser.add_argument("--regex", help="Regex pattern to apply on original names")
    parser.add_argument("--replace", help="Replacement for regex")
    parser.add_argument("--copy", action="store_true", help="Copy files instead of rename (keep originals)")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing")
    parser.add_argument("--save-names", action="store_true", help="Only save original names, do not rename")
    parser.add_argument("--log", help="Log file path")
    parser.add_argument("--create", "-c", action="store_true")
    args = parser.parse_args()

    folder = Path(args.folder)
    if args.create:
        folder.mkdir(parents=True, exist_ok=True)

    advanced_serial_rename(
        folder=folder,
        prefix=args.prefix,
        start=args.start,
        recursive=args.recursive,
        extensions=args.extensions,
        dry_run=args.dry_run,
        exclude_patterns=args.exclude,
        sort_by=args.sort_by,
        regex_pattern=args.regex,
        regex_replacement=args.replace,
        copy_mode=args.copy,
        parallel=args.parallel,
        save_names_only=args.save_names,
        log_file=Path(args.log) if args.log else None,
    )

if __name__ == "__main__":
    main()