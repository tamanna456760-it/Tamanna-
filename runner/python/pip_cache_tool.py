import subprocess
import sys
import os
from pathlib import Path

def run_pip_cache_command(*args):
    """Run a pip cache subcommand and return output."""
    cmd = [sys.executable, "-m", "pip", "cache"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout

def get_cache_info():
    """Show pip cache statistics."""
    output = run_pip_cache_command("info")
    if output:
        print("Pip cache info:")
        print(output)

def list_cached_packages():
    """List package names and versions stored in cache."""
    output = run_pip_cache_command("list")
    if output:
        print("Cached packages (format: package==version):")
        print(output)

def remove_all_cached_packages():
    """Clear the entire pip cache."""
    confirm = input("This will delete everything in pip cache. Continue? (y/n): ")
    if confirm.lower() == 'y':
        output = run_pip_cache_command("purge")
        if output:
            print("Cache cleared.")
            print(output)
    else:
        print("Aborted.")

def get_cache_directory():
    """Return the absolute path to pip's cache directory, or None if not found."""
    info = run_pip_cache_command("info")
    if info:
        for line in info.splitlines():
            if line.strip().startswith("Location:"):
                # Extract the path after "Location:"
                loc = line.split(":", 1)[1].strip()
                return Path(loc)
    return None

def list_cache_files():
    """List all files inside the cache directory directly (low‑level)."""
    cache_dir = get_cache_directory()
    if cache_dir and cache_dir.exists():
        print(f"Cache directory: {cache_dir}")
        for root, dirs, files in os.walk(cache_dir):
            rel_path = Path(root).relative_to(cache_dir)
            if rel_path == Path("."):
                print("Files in root:")
            else:
                print(f"\nIn {rel_path}:")
            for f in files:
                print(f"  {f}")
    else:
        print("Cache directory not found or not accessible.")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pip_cache_tool.py info      - Show cache info")
        print("  python pip_cache_tool.py list      - List cached packages")
        print("  python pip_cache_tool.py purge     - Remove all cache")
        print("  python pip_cache_tool.py files     - List all cache files")
        return

    command = sys.argv[1]
    if command == "info":
        get_cache_info()
    elif command == "list":
        list_cached_packages()
    elif command == "purge":
        remove_all_cached_packages()
    elif command == "files":
        list_cache_files()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()