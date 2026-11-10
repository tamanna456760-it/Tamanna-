#!/usr/bin/env python3
"""Explicit Tamanna maintenance commands with shell-free subprocess calls."""
import datetime
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "tamanna_master.log"
CONFIG = ROOT / "tamanna_master_config.json"


def log(message):
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(cmd, *, cwd=None, check=True):
    """Run an argument list without invoking a shell."""
    if not isinstance(cmd, (list, tuple)) or not cmd:
        raise ValueError("cmd must be a non-empty argument list")
    result = subprocess.run(
        [str(part) for part in cmd],
        cwd=str(cwd) if cwd is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.stdout.strip():
        log("OUT: " + result.stdout.strip())
    if result.stderr.strip():
        log("ERR: " + result.stderr.strip())
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {cmd[0]}")
    return result


def docker_up():
    compose_file = Path("docker-compose.yml").resolve()
    if not compose_file.is_file():
        raise FileNotFoundError(f"Docker Compose file not found: {compose_file}")
    run(["docker-compose", "-f", compose_file, "pull"], check=False)
    run(["docker-compose", "-f", compose_file, "up", "-d"])


def docker_down():
    compose_file = Path("docker-compose.yml").resolve()
    if not compose_file.is_file():
        raise FileNotFoundError(f"Docker Compose file not found: {compose_file}")
    run(["docker-compose", "-f", compose_file, "down"])


def backup(paths, archive_root="archives"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = Path(archive_root).expanduser().resolve() / f"backup_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=False)
    manifest = []

    for index, raw_path in enumerate(paths):
        source = Path(raw_path).expanduser().resolve()
        if not source.exists():
            log(f"[WARN] Missing path: {source}")
            continue
        target = archive_dir / f"{index}_{source.name}"
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
            item_type = "dir"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            item_type = "file"
        manifest.append({"type": item_type, "source": str(source), "dest": str(target)})

    (archive_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    archive_file = archive_dir.with_suffix(".tar.gz")
    with tarfile.open(archive_file, "w:gz") as archive:
        archive.add(archive_dir, arcname=archive_dir.name)
    log(f"Backup created: {archive_file}")
    return archive_file


def heartbeat_check(url="http://localhost:8000/health", timeout=5):
    try:
        with urlopen(url, timeout=timeout) as response:
            status = response.status
        log(f"Heartbeat {url} -> {status}")
        return status == 200
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        log(f"Heartbeat failed: {error}")
        return False


def _safe_sync_paths(values):
    if not isinstance(values, list) or not values:
        raise ValueError("sync_paths must be a non-empty list of relative paths")
    paths = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sync_paths entries must be non-empty strings")
        path = Path(value)
        parts = path.parts
        forbidden_names = {"credentials.json", "id_rsa", "id_ed25519", "token", "token.txt"}
        if (
            path.is_absolute()
            or not parts
            or value.strip() in {".", "./"}
            or ".." in parts
            or value.startswith(":")
            or any(char in value for char in "*?[]")
            or any(part == ".env" or part.startswith(".env.") for part in parts)
            or any(part.lower() in forbidden_names for part in parts)
            or any(Path(part).suffix.lower() in {".pem", ".key", ".p12", ".pfx"} for part in parts)
        ):
            raise ValueError(f"Unsafe or overly broad sync path: {value}")
        paths.append(path.as_posix())
    return paths


def git_sync(repo_path, remote="origin", branch="main", paths=None):
    """Explicit sync of configured paths only; never stages the whole repository."""
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository not found: {repo}")
    if branch != "main":
        raise ValueError("Only the main branch is permitted")
    allowed_paths = _safe_sync_paths(paths)

    run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    current_branch = run(
        ["git", "branch", "--show-current"], cwd=repo
    ).stdout.strip()
    if current_branch != "main":
        raise RuntimeError(f"Refusing to sync branch {current_branch!r}; expected 'main'")

    run(["git", "add", "--", *allowed_paths], cwd=repo)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=repo, check=False)
    if staged.returncode == 0:
        log(f"No staged changes for {repo}")
        return
    if staged.returncode != 1:
        raise RuntimeError("Unable to inspect staged changes")

    message = f"Tamanna explicit sync {datetime.datetime.now().isoformat(timespec='seconds')}"
    run(["git", "commit", "-m", message], cwd=repo)
    run(["git", "pull", "--rebase", remote, "main"], cwd=repo)
    run(["git", "push", remote, "main"], cwd=repo)
    log(f"Git sync completed for {repo}")


def main():
    if len(sys.argv) < 2:
        print("Usage: tamannna_master.py [up|down|backup|heartbeat|sync|status]")
        raise SystemExit(2)

    command = sys.argv[1]
    config = {}
    if CONFIG.exists():
        config = json.loads(CONFIG.read_text(encoding="utf-8"))

    if command == "up":
        docker_up()
    elif command == "down":
        docker_down()
    elif command == "backup":
        paths = config.get("backup_paths", ["./tamanna", "./panels", "./ssl"])
        backup(paths, config.get("archive_root", "./archives"))
    elif command == "heartbeat":
        healthy = heartbeat_check(
            config.get("health_url", "http://localhost:8000/health")
        )
        log("HEARTBEAT OK" if healthy else "HEARTBEAT FAIL")
        if not healthy:
            raise SystemExit(1)
    elif command == "sync":
        repositories = config.get("repos", [])
        if not repositories:
            raise ValueError("Configure an explicit non-empty 'repos' list before sync")
        sync_paths = config.get("sync_paths")
        for repository in repositories:
            git_sync(
                repository,
                config.get("git_remote", "origin"),
                config.get("git_branch", "main"),
                sync_paths,
            )
    elif command == "status":
        run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
    else:
        print(f"Unknown command: {command}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
