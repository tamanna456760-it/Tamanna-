"""Isolated six-worker supervisor-team execution using the Codex CLI."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, Cookie, HTTPException, Request
from pydantic import BaseModel, Field

from tamanna_ai.integrations.codex_bridge import (
    COOKIE,
    _admin_user,
    _workspace,
    check_origin,
    rate_limit_user_action,
)
from tamanna_ai.supervisors.registry import (
    DEFENSE_SPECIALISTS,
    SECTION_SPECIALISTS,
    SERVER_SPECIALISTS,
    build_supervisor_registry,
)

router = APIRouter(prefix="/api/supervisors", tags=["supervisors"])
LOGGER = logging.getLogger("tamanna.supervisors")
MAX_OUTPUT = 3000
DEFENSE_MAX_PARALLEL = 5
def _timeout_seconds() -> int:
    try:
        value = int(os.getenv("TAMANNA_SUPERVISOR_TIMEOUT", "600"))
    except (TypeError, ValueError):
        value = 600
    return max(60, min(900, value))


TIMEOUT_SECONDS = _timeout_seconds()


class SupervisorRunRequest(BaseModel):
    team_id: str = Field(min_length=2, max_length=80)
    prompt: str = Field(min_length=10, max_length=5000)
    write_access: bool = False
    confirm_write: bool = False


def _run_one(executable: str, workspace: Path, prompt: str, sandbox: str) -> dict:
    command = [
        executable, "exec", "--cd", str(workspace),
        "--sandbox", sandbox, "--ask-for-approval", "never",
        "--json", "--ephemeral", prompt,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=str(workspace),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "worker_timeout", "output": ""}
    except OSError:
        return {"ok": False, "error": "worker_start_failed", "output": ""}
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "output": (result.stdout or "")[-MAX_OUTPUT:],
    }


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(root), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        timeout=30, check=False, shell=False,
    )


def _team_definition(registry: dict, team_id: str):
    if team_id == "defense":
        return "Tamanna Defense and Security Team", DEFENSE_SPECIALISTS
    if team_id == "server_ops":
        return "Tamanna Server Operations Team", SERVER_SPECIALISTS
    section = registry["sections"].get(team_id)
    if not section:
        raise HTTPException(status_code=404, detail="Unknown supervisor team.")
    return section["name"], SECTION_SPECIALISTS


def _agent_prompt(team_name: str, role: str, responsibility: str, task: str, write: bool) -> str:
    mode = (
        "You are the sole implementation worker. Make focused code changes only in this isolated Git worktree. "
        "Do not commit, push, deploy, alter secrets, modify permission policy, or perform destructive operations. "
        "Run relevant safe tests and report every changed file."
        if write else
        "You are a read-only reviewer. Do not edit files, run destructive commands, deploy, or change permissions. "
        "Return concrete findings with file paths, evidence, severity, and recommended fixes."
    )
    return (
        f"Tamanna AI supervisor team: {team_name}.\nRole: {role}. Responsibility: {responsibility}.\n"
        f"{mode}\nUser task: {task}\n"
        "Accuracy rules: inspect source before conclusions; distinguish verified facts from hypotheses; "
        "never claim tests passed unless you ran them and observed success; identify missing evidence."
    )


async def _execute_team(payload: SupervisorRunRequest) -> dict:
    if os.getenv("TAMANNA_CODEX_ENABLED", "").strip().lower() != "true":
        raise HTTPException(status_code=503, detail="Codex supervisor runtime is disabled.")
    executable = shutil.which("codex")
    if not executable:
        raise HTTPException(status_code=503, detail="Codex CLI is not installed in the backend runtime.")
    if payload.team_id == "defense" and payload.write_access:
        raise HTTPException(status_code=403, detail="The 100-agent Cyber Defense Team is analysis-only; remediation must go through a separately approved implementation team and branch.")
    if payload.write_access:
        if not payload.confirm_write:
            raise HTTPException(status_code=400, detail="Explicit write confirmation is required.")
        if os.getenv("TAMANNA_CODEX_WRITE_ENABLED", "").strip().lower() != "true":
            raise HTTPException(status_code=403, detail="Supervisor write mode is disabled by server configuration.")

    root = _workspace()
    registry = build_supervisor_registry(root)
    team_name, specialists = _team_definition(registry, payload.team_id)
    lead_prompt = _agent_prompt(
        team_name, "team_lead", "Coordinate scope, verify specialist findings, and summarize outcomes.",
        payload.prompt, False,
    )
    specialist_prompts = [
        _agent_prompt(team_name, role, responsibility, payload.prompt,
                      payload.write_access and role == "implementation")
        for role, responsibility, _capability in specialists
    ]

    # Every task runs in a fresh Git worktree. A write task gets a new local branch;
    # no worker is given a GitHub token or permission to push/deploy.
    task_suffix = uuid.uuid4().hex[:12]
    branch_name = f"tamanna/supervisor-{task_suffix}" if payload.write_access else None
    worktree = root.parent / ".tamanna-supervisor-worktrees" / task_suffix
    worktree.parent.mkdir(parents=True, exist_ok=True)
    args = ["worktree", "add"]
    if branch_name:
        args += ["-b", branch_name]
    else:
        args += ["--detach"]
    args += [str(worktree), "HEAD"]
    created = await asyncio.to_thread(_git, root, *args)
    if created.returncode != 0:
        raise HTTPException(status_code=503, detail="Could not create an isolated Git worktree.")

    try:
        if payload.write_access:
            # One writer first; all five reviewers run read-only after it completes.
            writer_index = next(i for i, (role, _r, _c) in enumerate(specialists) if role == "implementation")
            writer = await asyncio.to_thread(
                _run_one, executable, worktree, specialist_prompts[writer_index], "workspace-write"
            )
            reviewer_prompts = [lead_prompt] + [
                specialist_prompts[i] for i in range(len(specialists)) if i != writer_index
            ]
            reviews = await asyncio.gather(*[
                asyncio.to_thread(_run_one, executable, worktree, prompt, "read-only")
                for prompt in reviewer_prompts
            ])
            results = [{"role": "implementation", **writer}]
            review_roles = ["team_lead"] + [
                role for i, (role, _r, _c) in enumerate(specialists) if i != writer_index
            ]
            results.extend({"role": role, **result} for role, result in zip(review_roles, reviews))
        else:
            prompts = [lead_prompt] + specialist_prompts
            roles = ["team_lead"] + [role for role, _r, _c in specialists]
            semaphore = asyncio.Semaphore(DEFENSE_MAX_PARALLEL if payload.team_id == "defense" else 5)

            async def run_bounded(prompt: str):
                async with semaphore:
                    return await asyncio.to_thread(_run_one, executable, worktree, prompt, "read-only")

            completed = await asyncio.gather(*(run_bounded(prompt) for prompt in prompts))
            results = [{"role": role, **result} for role, result in zip(roles, completed)]

        status = await asyncio.to_thread(_git, worktree, "status", "--short")
        changed = await asyncio.to_thread(_git, worktree, "diff", "--name-only")
        success = all(item.get("ok") for item in results)
        LOGGER.info(
            "supervisor_team_run team=%s write=%s workers=%s success=%s branch=%s",
            payload.team_id, payload.write_access, len(results), success, branch_name or "read-only",
        )
        return {
            "ok": success,
            "team_id": payload.team_id,
            "team_name": team_name,
            "workers_started": len(results),
            "agent_count_including_lead": len(results),
            "max_parallel_workers": DEFENSE_MAX_PARALLEL if payload.team_id == "defense" else 5,
            "workers_completed": len(results),
            "results": results,
            "sandbox": "workspace-write + read-only reviews" if payload.write_access else "read-only",
            "branch": branch_name,
            "worktree": str(worktree) if payload.write_access else None,
            "changed_files": [line for line in changed.stdout.splitlines() if line],
            "working_tree_status": [line for line in status.stdout.splitlines() if line],
            "defensive_only": payload.team_id == "defense",
            "github_push": False,
            "production_deployment": False,
        }
    finally:
        if not payload.write_access:
            await asyncio.to_thread(_git, root, "worktree", "remove", "--force", str(worktree))


@router.post("/run")
async def run_supervisor_team(
    payload: SupervisorRunRequest,
    request: Request,
    token: str | None = Cookie(default=None, alias=COOKIE),
):
    user = _admin_user(token)
    check_origin(request)
    rate_limit_user_action(user["id"], "supervisor_team_run", limit=1, window_seconds=600)
    return await _execute_team(payload)


__all__ = ["router"]
