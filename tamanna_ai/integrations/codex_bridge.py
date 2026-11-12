"""Admin-only, sandboxed bridge from Tamanna AI to the local Codex CLI.

Codex must be installed and authenticated in the backend runtime. The bridge never
uses a shell, never accepts a working-directory from the request, and defaults to
read-only execution. Workspace writes require a separate server-side opt-in.
"""
import asyncio
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Request
from pydantic import BaseModel, Field

from tamanna_ai.authentication.router import (
    COOKIE,
    check_origin,
    current_user,
    rate_limit_user_action,
)

router = APIRouter(prefix="/api/codex", tags=["codex"])
ROOT = Path(__file__).resolve().parents[2]
MAX_OUTPUT = 16000
TASK_TIMEOUT_SECONDS = max(30, min(900, int(os.getenv("TAMANNA_CODEX_TIMEOUT", "600"))))


class CodexTaskRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=8000)
    write_access: bool = False
    confirm_write: bool = False


def _admin_user(token: Optional[str]):
    user = current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Sign in required.")
    allowed = {
        item.strip().lower()
        for item in os.getenv("TAMANNA_ADMIN_EMAIL", "").split(",")
        if item.strip()
    }
    if not allowed:
        raise HTTPException(status_code=503, detail="Codex access is not configured for an admin.")
    if user.get("email", "").strip().lower() not in allowed:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def _workspace() -> Path:
    candidate = Path(os.getenv("TAMANNA_CODEX_WORKSPACE", str(ROOT))).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Codex workspace must be inside the Tamanna repository.") from exc
    if not candidate.is_dir():
        raise HTTPException(status_code=503, detail="Codex workspace directory is unavailable.")
    return candidate


@router.get("/status")
async def codex_status(token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    _admin_user(token)
    enabled = os.getenv("TAMANNA_CODEX_ENABLED", "").strip().lower() == "true"
    executable = shutil.which("codex")
    return {
        "enabled": enabled,
        "installed": bool(executable),
        "authenticated_runtime_required": True,
        "write_enabled": os.getenv("TAMANNA_CODEX_WRITE_ENABLED", "").strip().lower() == "true",
        "default_sandbox": "read-only",
    }


@router.post("/tasks")
async def run_codex_task(
    payload: CodexTaskRequest,
    request: Request,
    token: Optional[str] = Cookie(default=None, alias=COOKIE),
):
    user = _admin_user(token)
    check_origin(request)
    rate_limit_user_action(user["id"], "codex_task", limit=3, window_seconds=300)

    if os.getenv("TAMANNA_CODEX_ENABLED", "").strip().lower() != "true":
        raise HTTPException(status_code=503, detail="Codex bridge is disabled by server configuration.")
    executable = shutil.which("codex")
    if not executable:
        raise HTTPException(status_code=503, detail="Codex CLI is not installed in the backend runtime.")
    if payload.write_access:
        if not payload.confirm_write:
            raise HTTPException(status_code=400, detail="Explicit write confirmation is required.")
        if os.getenv("TAMANNA_CODEX_WRITE_ENABLED", "").strip().lower() != "true":
            raise HTTPException(status_code=403, detail="Codex workspace-write mode is disabled by server configuration.")

    workspace = _workspace()
    sandbox = "workspace-write" if payload.write_access else "read-only"
    command = [
        executable, "exec", "--cd", str(workspace),
        "--sandbox", sandbox, "--ask-for-approval", "never",
        "--json", "--ephemeral", payload.prompt,
    ]

    def _run():
        import subprocess
        try:
            completed = subprocess.run(
                command,
                cwd=str(workspace),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=TASK_TIMEOUT_SECONDS,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail="Codex task timed out.") from exc
        return completed

    result = await asyncio.to_thread(_run)
    # Do not return stderr, environment values, or authentication diagnostics.
    output = (result.stdout or "").strip()
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "sandbox": sandbox,
        "workspace": str(workspace.relative_to(ROOT)),
        "output": output[-MAX_OUTPUT:],
    }


__all__ = ["router"]
