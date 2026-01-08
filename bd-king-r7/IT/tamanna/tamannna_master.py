#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "tamanna_master.log"
CONFIG = ROOT / "tamanna_master_config.json"

def log(msg):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run(cmd, check=True):
    log(f"CMD: {cmd}")
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.stdout:
        log("OUT: " + res.stdout.strip())
    if res.stderr:
        log("ERR: " + res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return res

def docker_up():
    run("docker-compose -f docker-compose.yml pull || true")
    run("docker-compose -f docker-compose.yml up -d")

def docker_down():
    run("docker-compose -f docker-compose.yml down")

def backup(paths, archive_root="archives"):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(archive_root) / f"backup_{ts}"
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    for p in paths:
        p = Path(p).expanduser()
        if not p.exists():
            log(f"[WARN] Missing path {p}")
            continue
        target = dest / p.name
        if p.is_dir():
            run(f"rsync -a --delete {p}/ {target}/", check=False)
            manifest.append({"type":"dir","source":str(p),"dest":str(target)})
        else:
            run(f"cp -a {p} {target}", check=False)
            manifest.append({"type":"file","source":str(p),"dest":str(target)})
    with open(dest / "MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    run(f"tar -czf {dest}.tar.gz -C {dest.parent} {dest.name}")
    log(f"Backup created {dest}.tar.gz")

def heartbeat_check(url="http://localhost:8000/health"):
    try:
        res = run(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", check=False)
        code = res.stdout.strip()
        log(f"Heartbeat {url} -> {code}")
        return code == "200"
    except Exception as e:
        log(f"Heartbeat error {e}")
        return False

def git_sync(repo_path, remote="origin", branch="main"):
    repo = Path(repo_path)
    if not repo.exists():
        log(f"[ERROR] Repo missing {repo}")
        return
    run(f"cd {repo} && git add -A && git commit -m 'auto commit {datetime.datetime.now().isoformat()}' || true")
    run(f"cd {repo} && git pull {remote} {branch} --rebase || true")
    run(f"cd {repo} && git push {remote} {branch} || true")
    log(f"Git sync done for {repo}")

def main():
    if len(sys.argv) < 2:
        print("Usage: tamanna_master.py [up|down|backup|heartbeat|sync|status]")
        sys.exit(1)
    cmd = sys.argv[1]
    cfg = {}
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cmd == "up":
        docker_up()
    elif cmd == "down":
        docker_down()
    elif cmd == "backup":
        paths = cfg.get("backup_paths", ["./tamanna", "./panels", "./ssl", "./gmail_exports"])
        backup(paths, cfg.get("archive_root","./archives"))
    elif cmd == "heartbeat":
        ok = heartbeat_check(cfg.get("health_url","http://localhost:8000/health"))
        log("HEARTBEAT OK" if ok else "HEARTBEAT FAIL")
    elif cmd == "sync":
        repos = cfg.get("repos", ["./tamanna", "./panels"])
        for r in repos:
            git_sync(r, cfg.get("git_remote","origin"), cfg.get("git_branch","main"))
    elif cmd == "status":
        run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
