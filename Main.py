from pathlib import Path
import json
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CHAT_FILE = DATA_DIR / "chat_history.json"


# ============================================================
# CREATE JSON FILE
# ============================================================

if not CHAT_FILE.exists():

    CHAT_FILE.write_text(
        "[]",
        encoding="utf-8"
    )


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Tamanna AI",
    version="1.0.0"
)

# ============================================================
# TAMANNA SKILL SYSTEM V1
# ============================================================

try:
    from pathlib import Path

    from tamanna_ai.skills import (
        TamannaSkillManager,
    )

    TAMANNA_SKILLS = TamannaSkillManager(
        Path(__file__).resolve().parent
    )

    @app.get("/api/skills")
    async def tamanna_skills():
        skills = TAMANNA_SKILLS.list_skills()

        return {
            "status": "online",
            "count": len(skills),
            "skills": [
                {
                    "name": skill["name"],
                    "description": skill["description"],
                    "path": skill["path"],
                }
                for skill in skills
            ],
        }

    @app.post("/api/skills/match")
    async def tamanna_skill_match(
        payload: dict,
    ):
        query = str(
            payload.get("query")
            or payload.get("task")
            or ""
        ).strip()

        if not query:
            return {
                "status": "error",
                "error": "query is required",
            }

        matches = TAMANNA_SKILLS.match(
            query
        )

        return {
            "status": "ok",
            "query": query,
            "matches": matches,
        }

    @app.get("/api/skills/interview")
    async def tamanna_skill_interview():
        return {
            "status": "ok",
            "questions": (
                TAMANNA_SKILLS.interview()
            ),
        }

    @app.post("/api/skills/create")
    async def tamanna_skill_create(
        payload: dict,
    ):
        interview = payload.get(
            "interview"
        )

        if not isinstance(interview, dict):
            return {
                "status": "error",
                "error": "interview object is required",
            }

        return TAMANNA_SKILLS.create_skill(
            interview,
            overwrite=(
                payload.get("overwrite")
                is True
            ),
        )

    @app.post("/api/skills/test")
    async def tamanna_skill_test(
        payload: dict,
    ):
        path = payload.get("path")

        if not path:
            return {
                "status": "error",
                "error": "path is required",
            }

        return TAMANNA_SKILLS.test_skill(
            path
        )

    @app.post("/api/skills/refine")
    async def tamanna_skill_refine(
        payload: dict,
    ):
        path = payload.get("path")
        correction = payload.get(
            "correction"
        )

        if not path:
            return {
                "status": "error",
                "error": "path is required",
            }

        if not isinstance(
            correction,
            str,
        ):
            return {
                "status": "error",
                "error": "correction is required",
            }

        return TAMANNA_SKILLS.refine_skill(
            path,
            correction,
        )

    print(
        "[TAMANNA AI] Skill System: ONLINE"
    )

except Exception as exc:
    TAMANNA_SKILLS = None

    print(
        "[TAMANNA AI] Skill System ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END TAMANNA SKILL SYSTEM V1
# ============================================================


# ============================================================
# TAMANNA INTELLIGENT CODE BUILDER V1
# ============================================================

try:
    from tamanna_ai.code_builder import (
        IntelligentCodeBuilder,
    )

    TAMANNA_CODE_BUILDER = IntelligentCodeBuilder(
        Path(__file__).resolve().parent
    )

    @app.get("/api/code-builder/status")
    async def code_builder_status():
        return {
            "status": "online",
            "engine": "Tamanna Intelligent Code Builder",
            "project_root": str(
                TAMANNA_CODE_BUILDER.project_root
            ),
        }

    @app.get("/api/code-builder/scan")
    async def code_builder_scan():
        return TAMANNA_CODE_BUILDER.scan_project()

    @app.post("/api/code-builder/inspect")
    async def code_builder_inspect(
        payload: dict,
    ):
        path = payload.get("path")

        if not path:
            return {
                "status": "error",
                "error": "path is required",
            }

        return TAMANNA_CODE_BUILDER.inspect(path)

    @app.post("/api/code-builder/propose")
    async def code_builder_propose(
        payload: dict,
    ):
        path = payload.get("path")
        content = payload.get("content")

        if not path:
            return {
                "status": "error",
                "error": "path is required",
            }

        if not isinstance(content, str):
            return {
                "status": "error",
                "error": "content must be a string",
            }

        return TAMANNA_CODE_BUILDER.propose_write(
            path,
            content,
        )

    @app.post("/api/code-builder/apply")
    async def code_builder_apply(
        payload: dict,
    ):
        path = payload.get("path")
        content = payload.get("content")
        confirm = payload.get("confirm") is True

        if not path:
            return {
                "status": "error",
                "error": "path is required",
            }

        if not isinstance(content, str):
            return {
                "status": "error",
                "error": "content must be a string",
            }

        return TAMANNA_CODE_BUILDER.apply_write(
            path,
            content,
            confirm=confirm,
        )

    print(
        "[TAMANNA AI] Intelligent Code Builder: ONLINE"
    )

except Exception as exc:
    TAMANNA_CODE_BUILDER = None

    print(
        "[TAMANNA AI] Intelligent Code Builder ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END TAMANNA INTELLIGENT CODE BUILDER V1
# ============================================================



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# STATIC FILES
# ============================================================

CSS_DIR = BASE_DIR / "css"
JS_DIR = BASE_DIR / "js"


if CSS_DIR.exists():

    app.mount(
        "/css",
        StaticFiles(directory=CSS_DIR),
        name="css"
    )


if JS_DIR.exists():

    app.mount(
        "/js",
        StaticFiles(directory=JS_DIR),
        name="js"
    )


# ============================================================
# INDEX
# ============================================================

@app.get("/")
async def index():

    index_file = BASE_DIR / "index.html"

    if not index_file.exists():

        return {
            "error": "index.html পাওয়া যায়নি"
        }

    return FileResponse(index_file)


# ============================================================
# STATUS
# ============================================================

@app.get("/api/status")
async def status():

    return {
        "status": "online",
        "server": "main.py",
        "assistant": "Tamanna AI",
        "chat_storage": str(CHAT_FILE)
    }


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_history():

    try:

        data = json.loads(
            CHAT_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data

    except Exception as error:

        print(
            f"[JSON] Read error: {error}"
        )

    return []


# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(user_message, ai_reply):

    history = load_history()

    history.append({
        "time": datetime.now().isoformat(),
        "user": user_message,
        "assistant": ai_reply
    })

    CHAT_FILE.write_text(
        json.dumps(
            history,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"[JSON] Saved -> {CHAT_FILE}"
    )



# ============================================================
# FILE ACTION BRIDGE
# ============================================================

try:
    from modules.tamanna.action.file_action_bridge import (
        route_file_action,
    )

    _tamanna_file_action_bridge = route_file_action

    print(
        "[TAMANNA AI] File Action Bridge: ATTACHED"
    )

except Exception as exc:

    _tamanna_file_action_bridge = None

    print(
        "[TAMANNA AI] File Action Bridge unavailable: "
        f"{type(exc).__name__}: {exc}"
    )


def _tamanna_try_file_action(
    message,
    confirmed=False,
):
    """
    Try local file/code actions before normal chat fallback.
    """

    if _tamanna_file_action_bridge is None:
        return None

    try:

        result = _tamanna_file_action_bridge(
            message,
            confirmed=confirmed,
        )

        return result

    except Exception as exc:

        print(
            "[FILE ACTION] Error: "
            f"{type(exc).__name__}: {exc}"
        )

        return {
            "ok": False,
            "status": "error",
            "reply": (
                "File action চালাতে সমস্যা হয়েছে।"
            ),
            "error": str(exc),
        }


# ============================================================
# BASIC AI
# ============================================================

def generate_reply(message):

    text = message.strip().lower()


    if text in [
        "hi",
        "hello",
        "hey",
        "হাই",
        "হ্যালো"
    ]:

        return (
            "হাই! 🥰\n"
            "আমি Tamanna AI।\n"
            "আপনার মেসেজ main.py থেকে পেয়েছি।"
        )


    if (
        "কেমন আছ" in text
        or "how are you" in text
    ):

        return (
            "আমি ভালো আছি। 😊\n"
            "আপনার সাথে কথা বলতে প্রস্তুত।"
        )


    if (
        "তোমার নাম" in text
        or "your name" in text
    ):

        return (
            "আমার নাম Tamanna AI। 🤖🥰"
        )


    if (
        "ধন্যবাদ" in text
        or "thanks" in text
    ):

        return (
            "আপনাকেও ধন্যবাদ। ❤️"
        )


    return (
        "আপনার মেসেজটি পেয়েছি। 😊\n\n"
        f"আপনি লিখেছেন:\n{message}"
    )


# ============================================================
# CHAT ACTION LAYER
# ============================================================

try:
    from data.chat_action.natural_action_router import (
        route_chat_action,
    )

    print("[TAMANNA AI] Natural Chat Action Layer: ONLINE")

except Exception as exc:
    route_chat_action = None

    print(
        "[TAMANNA AI] Natural Chat Action Layer ERROR:",
        exc,
    )


# ============================================================
# CHAT API
# ============================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):

    message = request.message.strip()


    if not message:

        return {
            "reply": "দয়া করে একটি মেসেজ লিখুন।"
        }


    print(
        f"[CHAT] User -> {message}"
    )


    # ========================================================
    # NATURAL CHAT ACTION EXECUTION
    # ========================================================
    try:
        if route_chat_action is not None:

            action_result = await route_chat_action(
                message
            )

            if action_result is not None:
                print(
                    "[CHAT ACTION] "
                    f"{action_result.get('intent', 'unknown')} "
                    "-> "
                    f"{action_result.get('reply', '')[:200]}"
                )

                action_reply = str(
                    action_result.get(
                        "reply",
                        "Action completed."
                    )
                )

                save_chat(
                    message,
                    action_reply
                )

                return {
                    "reply": action_reply,
                    "handled": True,
                    "source": "action_router",
                    "intent": action_result.get(
                        "intent",
                        "unknown"
                    ),
                    "action_result": action_result,
                }

    except Exception as exc:

        print(
            "[TAMANNA AI] Natural Chat Action failed: "
            f"{type(exc).__name__}: {exc}"
        )

        # Normal Master Response continues below.


    # ========================================================
    # MASTER RESPONSE PIPELINE
    # ========================================================
    try:
        master_result = await tamanna_master_response(message)

        reply = _tamanna_extract_reply(master_result)

        if not reply.strip():
            reply = "দুঃখিত, Tamanna AI কোনো উত্তর তৈরি করতে পারেনি।"

    except Exception as exc:
        print(
            "[TAMANNA AI] Master response failed: "
            f"{type(exc).__name__}: {exc}"
        )

        # Existing response engine remains as fallback.
        reply = generate_reply(message)

    print(
        f"[CHAT] AI -> {reply}"
    )

    # Auto save JSON
    save_chat(
        message,
        reply
    )

    return {
        "reply": reply
    }


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("🥰 Tamanna AI")
    print("Python Main Server")
    print("=" * 50)

    print(
        f"Project: {BASE_DIR}"
    )

    print(
        f"Chat JSON: {CHAT_FILE}"
    )

    print(
        "Server: http://127.0.0.1:8000"
    )

    print("=" * 50)


    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

# ============================================================
# TAMANNA AI DYNAMIC MODULE BRIDGE
# ============================================================

try:
    from modules.tamanna.module_router import (
        generate_tamanna_reply,
        reload_tamanna_modules,
    )

    # Dynamic module response engine.
    # Existing main.py code is preserved.
    generate_reply = generate_tamanna_reply

    print("[TAMANNA AI] Dynamic Module Router: ONLINE")

except Exception as exc:
    print(
        f"[TAMANNA AI] Dynamic Module Router failed: {exc}"
    )

# ============================================================
# TAMANNA AI DYNAMIC MODULE BRIDGE
# ============================================================
#
# Existing main.py code is preserved.
# New modules are automatically discovered from:
# modules/tamanna/modules/
#
# User-facing identity: Tamanna AI
#

try:
    from modules.tamanna.module_bridge import tamanna_ai_reply

    _tamanna_legacy_generate_reply = generate_reply

    def generate_reply(message):
        dynamic_reply = tamanna_ai_reply(message)

        if dynamic_reply is not None:
            return dynamic_reply

        return _tamanna_legacy_generate_reply(message)

    print("[TAMANNA AI] Dynamic Module Bridge: ONLINE")

except Exception as exc:
    print(
        f"[TAMANNA AI] Dynamic Module Bridge unavailable: {exc}"
    )


# ============================================================
# TAMANNA AI ASYNC RESPONSE COMPATIBILITY LAYER
# Added only - existing code is preserved.
# ============================================================

import asyncio
import inspect
import threading


def _tamanna_run_async_safely(awaitable):
    """
    Run an async Tamanna AI result from the existing
    synchronous generate_reply() interface.

    A separate thread is used because /api/chat itself
    already runs inside an asyncio event loop.
    """

    result_box = {
        "result": None,
        "error": None,
    }

    def runner():
        try:
            result_box["result"] = asyncio.run(
                awaitable
            )
        except Exception as exc:
            result_box["error"] = exc

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()
    thread.join()

    if result_box["error"] is not None:
        raise result_box["error"]

    return result_box["result"]


# Preserve whatever generate_reply currently points to.
_tamanna_previous_generate_reply = generate_reply


def generate_reply(message):
    """
    Async-safe wrapper around the existing Tamanna AI
    dynamic response system.

    Existing generate_reply logic is preserved.
    """

    try:

        # Prefer the new async-safe module bridge.
        from modules.tamanna.module_bridge import (
            tamanna_ai_reply_async,
        )

        result = tamanna_ai_reply_async(
            message
        )

        if inspect.isawaitable(result):

            result = _tamanna_run_async_safely(
                result
            )

        # Normalize dictionary response.
        if isinstance(result, dict):

            return result

        return {
            "ok": True,
            "type": "chat",
            "reply": str(result),
            "module": "chat",
            "source": "tamanna_ai",
        }

    except Exception as async_exc:

        print(
            "[TAMANNA AI] Async bridge failed: "
            f"{type(async_exc).__name__}: "
            f"{async_exc}"
        )

        # Fall back to the existing system.
        try:

            result = _tamanna_previous_generate_reply(
                message
            )

            if inspect.isawaitable(result):

                result = _tamanna_run_async_safely(
                    result
                )

            return result

        except Exception as fallback_exc:

            print(
                "[TAMANNA AI] Legacy fallback failed: "
                f"{type(fallback_exc).__name__}: "
                f"{fallback_exc}"
            )

            return {
                "ok": False,
                "type": "error",
                "reply": (
                    "Tamanna AI উত্তর তৈরি করতে "
                    "সমস্যা হয়েছে।"
                ),
                "error": str(fallback_exc),
                "module": "chat",
                "source": "tamanna_ai",
            }


print(
    "[TAMANNA AI] Async Response Compatibility: ONLINE"
)


# ============================================================
# TAMANNA AI PROJECT CONTEXT + RESPONSE ADAPTER
# Added without removing existing code.
# ============================================================

try:

    from modules.tamanna.project_context_adapter import (
        build_project_context,
        format_response,
    )

    print(
        "[TAMANNA AI] Project Context Adapter: ONLINE"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Project Context Adapter failed: "
        f"{exc}"
    )


def tamanna_format_chat_response(
    result,
    message,
):

    try:

        return format_response(
            result,
            message,
        )

    except Exception as exc:

        return {
            "ok": False,
            "type": "error",
            "reply": (
                "Tamanna AI response format করতে "
                "সমস্যা হয়েছে।"
            ),
            "error": str(exc),
            "module": "chat",
            "source": "tamanna_ai",
        }


def tamanna_project_context(
    message,
):

    try:

        return build_project_context(
            BASE_DIR,
            message,
        )

    except Exception as exc:

        print(
            "[TAMANNA CONTEXT] Scan failed: "
            f"{exc}"
        )

        return {
            "project_root": str(BASE_DIR),
            "total_files": 0,
            "relevant_files": [],
        }


print(
    "[TAMANNA AI] Project-wide Context System: ONLINE"
)


# ============================================================
# TAMANNA AI FINAL CHAT RESPONSE ADAPTER
# ADDITIVE ONLY - EXISTING CODE IS PRESERVED
# ============================================================

import asyncio
import inspect
import threading


def _tamanna_execute_async(awaitable):
    """
    Execute an async Tamanna AI operation safely
    even when /api/chat is already inside an event loop.
    """

    result_box = {
        "value": None,
        "error": None,
    }

    def _runner():

        try:
            result_box["value"] = asyncio.run(
                awaitable
            )

        except Exception as exc:
            result_box["error"] = exc

    worker = threading.Thread(
        target=_runner,
        daemon=True,
    )

    worker.start()
    worker.join()

    if result_box["error"] is not None:
        raise result_box["error"]

    return result_box["value"]


def _tamanna_extract_reply(result):
    """
    Convert every supported Tamanna AI result
    into a clean text response for HTML/JavaScript.
    """

    if isinstance(result, dict):

        reply = result.get("reply")

        if reply is None:
            reply = result.get("message")

        if reply is None:
            reply = result.get("content")

        if reply is None:
            reply = result.get("text")

        if reply is None:
            reply = ""

        return str(reply)

    if result is None:
        return ""

    return str(result)


# Preserve the currently configured response engine.
_tamanna_existing_generate_reply = generate_reply


def generate_reply(message):
    """
    Final synchronous interface used by /api/chat.

    Internally it executes Tamanna AI's async router
    and returns ONLY clean text to the API.
    """

    try:

        from modules.tamanna.module_router import (
            generate_tamanna_reply_async,
        )

        async_result = generate_tamanna_reply_async(
            message
        )

        if inspect.isawaitable(async_result):

            result = _tamanna_execute_async(
                async_result
            )

        else:

            result = async_result

        reply = _tamanna_extract_reply(
            result
        )

        if reply.strip():

            return reply

    except Exception as exc:

        print(
            "[TAMANNA AI] Async response adapter failed: "
            f"{type(exc).__name__}: {exc}"
        )

    # Existing AI remains as fallback.
    try:

        result = _tamanna_existing_generate_reply(
            message
        )

        if inspect.isawaitable(result):

            result = _tamanna_execute_async(
                result
            )

        return _tamanna_extract_reply(
            result
        )

    except Exception as exc:

        print(
            "[TAMANNA AI] Response fallback failed: "
            f"{type(exc).__name__}: {exc}"
        )

        return (
            "দুঃখিত, Tamanna AI এখন "
            "উত্তর তৈরি করতে পারেনি।"
        )


print(
    "[TAMANNA AI] Final Chat Response Adapter: ONLINE"
)


# ============================================================
# TAMANNA AI MESSAGE MEMORY API
# ADDITIVE ONLY — EXISTING CODE PRESERVED
# ============================================================

try:

    from modules.tamanna.message_api import router as message_memory_router

    app.include_router(
        message_memory_router
    )

    print(
        "[TAMANNA AI] Message Memory API: ATTACHED"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Message Memory API attach failed: "
        f"{type(exc).__name__}: {exc}"
    )


# ============================================================
# TAMANNA AI INDEXED CHAT MEMORY BRIDGE
# ADDITIVE ONLY — EXISTING CODE PRESERVED
# ============================================================

try:

    from modules.tamanna.message_memory import (
        search_message_fast,
    )

    _original_generate_reply_for_memory = generate_reply


    def generate_reply_with_memory(message):

        # 1. Search approved message memory first.
        memory_result = search_message_fast(
            message
        )

        # Runtime safety: memory search may return
        # dict, list, tuple, or None.
        memory_result = tamanna_normalize_memory_result(
            memory_result
        )

        if memory_result is not None:

            reply = memory_result.get(
                "reply"
            )

            if reply:

                print(
                    "[CHAT MEMORY] "
                    f"Matched -> {memory_result.get('category', 'general')}"
                )

                return {
                    "ok": True,
                    "type": "chat",
                    "reply": str(reply),
                    "module": "message_memory",
                    "source": "tamanna_ai_memory",
                    "category": memory_result.get(
                        "category",
                        "general"
                    ),
                }

        # 2. If memory has no answer,
        #    continue with the existing AI system.
        return _original_generate_reply_for_memory(
            message
        )


    generate_reply = generate_reply_with_memory

    print(
        "[TAMANNA AI] Chat Memory → AI Bridge: ONLINE"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Chat Memory Bridge failed: "
        f"{type(exc).__name__}: {exc}"
    )



# ============================================================
# TAMANNA AI — MASTER RESPONSE ENTRY
# ============================================================

try:
    from modules.tamanna.master_response_controller import (
        tamanna_master_response,
    )

    async def _master_chat_response(message: str):
        return await tamanna_master_response(message)

    print("[TAMANNA AI] Master Response Entry: ONLINE")

except Exception as exc:
    print(
        "[TAMANNA AI] Master Response Entry unavailable: "
        f"{type(exc).__name__}: {exc}"
    )

# ============================================================
# TAMANNA AI — MASTER RESPONSE API BRIDGE
# This makes /api/chat use the Master Response Controller.
# ============================================================

try:
    from modules.tamanna.master_response_controller import (
        tamanna_master_response,
    )

    @app.post("/api/chat/master")
    async def master_chat(request: ChatRequest):
        message = request.message.strip()

        if not message:
            return {
                "ok": False,
                "type": "chat",
                "reply": "দয়া করে একটি message লিখুন।",
                "source": "master_response",
            }

        print(
            f"[MASTER API] User -> {message}"
        )

        result = await tamanna_master_response(
            message
        )

        print(
            f"[MASTER API] Result -> {result}"
        )

        if isinstance(result, dict):
            reply = result.get("reply", "")
        else:
            reply = str(result)

        return {
            "ok": True,
            "type": "chat",
            "reply": str(reply),
            "source": "master_response",
            "result": result,
        }

    print(
        "[TAMANNA AI] Master Response API: ONLINE"
    )

except Exception as exc:
    print(
        "[TAMANNA AI] Master Response API failed: "
        f"{type(exc).__name__}: {exc}"
    )


# ============================================================
# TAMANNA AI — LINUX TOOL API
# ADDITIVE ONLY
# ============================================================

try:
    from data.linux.tool_manager import linux_tools

    @app.get("/api/linux/tools")
    async def linux_tools_api():
        return {
            "ok": True,
            "system": linux_tools.system,
            "tools": linux_tools.tools(),
        }


    @app.post("/api/linux/run")
    async def linux_run_api(payload: dict):
        command = str(
            payload.get("command", "")
        ).strip()

        return linux_tools.run(command)


    @app.get("/api/linux/status")
    async def linux_status_api():
        return {
            "ok": True,
            "system": linux_tools.system,
            "tools_available": len(
                linux_tools.tools()
            ),
        }


    print(
        "[TAMANNA AI] Linux Tool Manager: ONLINE"
    )

except Exception as exc:
    print(
        "[TAMANNA AI] Linux Tool Manager failed:",
        type(exc).__name__,
        exc,
    )


# ============================================================
# TAMANNA AI — AUTONOMOUS SECURITY TOOL DISCOVERY
# ADDITIVE ONLY
# ============================================================

try:
    from data.security.kali_tool_manager import kali_tools

    @app.get("/api/security/tools")
    async def security_tools():
        return kali_tools.discover()

    print(
        "[TAMANNA AI] Kali Security Tool Discovery: ONLINE"
    )

except Exception as exc:
    print(
        "[TAMANNA AI] Security Tool Discovery failed:",
        type(exc).__name__,
        exc,
    )


# ============================================================
# TAMANNA AI — AUTONOMOUS SELF-IMPROVEMENT
# ADDITIVE ONLY
# ============================================================

try:
    from data.self_improvement.engine import self_improvement

    @app.get("/api/self-improvement/status")
    async def self_improvement_status():
        return self_improvement.status()

    @app.post("/api/self-improvement/analyze")
    async def self_improvement_analyze():
        return self_improvement.analyze()

    print(
        "[TAMANNA AI] Self-Improvement Engine: ONLINE"
    )

except Exception as exc:
    print(
        "[TAMANNA AI] Self-Improvement Engine failed:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# TAMANNA AI — UNIFIED SYSTEM CONTROLLER
# ============================================================

try:
    from data.system.system_controller import tamanna_system

    @app.get("/api/tamanna/system")
    async def tamanna_system_overview():
        return tamanna_system.overview()

    print("[TAMANNA AI] Unified System Controller: ONLINE")

except Exception as e:
    print(f"[TAMANNA AI] Unified System Controller ERROR: {e}")

# ============================================================
# TAMANNA AI — LINUX SHELL + SELF HEALING BRIDGE
# ============================================================

try:
    from data.linux.shell_bridge import shell_bridge
    from data.self_healing.engine import self_healing

    @app.get("/api/linux/shell/status")
    async def linux_shell_status():
        return {
            "online": True,
            "project_root": str(shell_bridge.root),
            "mode": "controlled"
        }

    @app.post("/api/linux/shell")
    async def linux_shell(payload: dict):
        command = str(payload.get("command", "")).strip()

        return shell_bridge.run(command)

    @app.get("/api/self-healing/status")
    async def self_healing_status():
        return self_healing.status()

    @app.post("/api/self-healing/diagnose")
    async def self_healing_diagnose():
        return self_healing.analyze()

    @app.post("/api/self-healing/cycle")
    async def self_healing_cycle():
        return self_healing.cycle()

    print("[TAMANNA AI] Linux Shell Bridge: ONLINE")
    print("[TAMANNA AI] Self-Healing Engine: ONLINE")

except Exception as e:
    print("[TAMANNA AI] Shell/Self-Healing load error:", e)


# ============================================================
# TAMANNA AI — AUTONOMOUS PROJECT BRAIN
# ============================================================

try:

    from data.autonomous.project_brain import project_brain

    @app.get("/api/autonomous/think")
    async def autonomous_think():

        return project_brain.think()

    @app.get("/api/autonomous/files")
    async def autonomous_files():

        return {
            "root": str(project_brain.root),
            "files": project_brain.discover_files()
        }

    print("[TAMANNA AI] Autonomous Project Brain: ONLINE")

except Exception as e:

    print(
        "[TAMANNA AI] Autonomous Project Brain ERROR:",
        e
    )


# ============================================================
# TAMANNA AI — AUTONOMOUS STARTUP SCAN
# ============================================================

try:
    from data.autonomous.project_brain import project_brain

    AUTONOMOUS_STARTUP_STATE = {
        "status": "starting"
    }

    try:
        AUTONOMOUS_STARTUP_STATE["result"] = project_brain.think()
        AUTONOMOUS_STARTUP_STATE["status"] = "ready"

        result = AUTONOMOUS_STARTUP_STATE["result"]

        print(
            "[TAMANNA AI] Autonomous Scan: "
            f"{result['project']['files']} files discovered"
        )

        print(
            "[TAMANNA AI] Autonomous Needs: "
            f"{len(result['needs'])}"
        )

    except Exception as scan_error:

        AUTONOMOUS_STARTUP_STATE = {
            "status": "error",
            "error": str(scan_error)
        }

        print(
            "[TAMANNA AI] Autonomous Scan ERROR:",
            scan_error
        )

except Exception as import_error:

    AUTONOMOUS_STARTUP_STATE = {
        "status": "error",
        "error": str(import_error)
    }

    print(
        "[TAMANNA AI] Autonomous Brain ERROR:",
        import_error
    )


@app.get("/api/autonomous/startup")
async def autonomous_startup():

    return AUTONOMOUS_STARTUP_STATE


# ============================================================
# TAMANNA AI — AUTONOMOUS PLANNER + SAFE BUILDER
# ============================================================

try:

    from data.autonomous.planner import autonomous_planner
    from data.autonomous.builder import safe_builder

    @app.get("/api/autonomous/plans")
    async def autonomous_plans():

        return {
            "plans": autonomous_planner.status()
        }

    @app.post("/api/autonomous/plan")
    async def autonomous_make_plan():

        brain = project_brain.think()

        plans = autonomous_planner.create_plan(brain)

        return {
            "ok": True,
            "plans": plans
        }

    @app.post("/api/autonomous/build")
    async def autonomous_build(payload: dict):

        plan = payload.get("plan")

        if not isinstance(plan, dict):
            return {
                "ok": False,
                "error": "plan object required"
            }

        # Explicit approval required for creation.
        if payload.get("confirm") is not True:
            return {
                "ok": False,
                "requires_confirmation": True,
                "message": "Send confirm=true to create scaffold"
            }

        return safe_builder.build(plan)

    print("[TAMANNA AI] Autonomous Planner: ONLINE")
    print("[TAMANNA AI] Safe Builder: ONLINE")

except Exception as e:

    print(
        "[TAMANNA AI] Autonomous Planner/Builder ERROR:",
        e
    )


# ============================================================
# TAMANNA AI — AUTONOMOUS REPAIR ENGINE
# ============================================================

try:

    from data.autonomous.repair_engine import repair_engine

    @app.get("/api/autonomous/repair/status")
    async def autonomous_repair_status():
        return repair_engine.status()

    @app.post("/api/autonomous/repair")
    async def autonomous_repair():
        return repair_engine.diagnose_and_repair()

    @app.get("/api/autonomous/repair/history")
    async def autonomous_repair_history():
        return {
            "history": repair_engine.history()
        }

    print(
        "[TAMANNA AI] Autonomous Repair Engine: ONLINE"
    )

except Exception as e:

    print(
        "[TAMANNA AI] Repair Engine ERROR:",
        e
    )


# ============================================================
# TAMANNA_AUTONOMOUS_CORE_V1
# ============================================================

try:

    from data.autonomous.master import (
        tamanna_autonomous
    )

    # Automatic startup scan
    AUTONOMOUS_STARTUP = (
        tamanna_autonomous.think()
    )

    @app.get("/api/autonomous/status")
    async def autonomous_status():

        return tamanna_autonomous.status()


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/think is registered by project_brain.
    # Original implementation intentionally preserved below.
    async def autonomous_think_legacy():

        return tamanna_autonomous.think()


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/files is registered by project_brain.
    # Original implementation intentionally preserved.
    async def autonomous_files_legacy():

        scan = tamanna_autonomous.scan()

        return {
            "root": str(
                tamanna_autonomous.root
            ),
            "total_files": scan[
                "total_files"
            ],
            "extensions": scan[
                "extensions"
            ],
            "files": scan[
                "files"
            ]
        }


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/plans is registered above.
    # Original implementation intentionally preserved.
    async def autonomous_plans_legacy():

        return {
            "plans": tamanna_autonomous.load(
                tamanna_autonomous.root
                / "data/autonomous/plans.json",
                []
            )
        }


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/build is registered by Safe Builder.
    # Original implementation intentionally preserved.
    async def autonomous_build_legacy(
        payload: dict
    ):

        plan = payload.get("plan")

        if not isinstance(
            plan,
            dict
        ):

            return {
                "ok": False,
                "error": "plan required"
            }

        return tamanna_autonomous.build(
            plan,
            confirm=(
                payload.get("confirm")
                is True
            )
        )


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/repair/status is registered above.
    # Original implementation intentionally preserved.
    async def autonomous_repair_status_legacy():

        return {
            "online": True,
            "state": tamanna_autonomous.state,
            "history": tamanna_autonomous.load(
                tamanna_autonomous.root
                / "data/autonomous/history.json",
                []
            )
        }


    # LEGACY ROUTE DISABLED:
    # Canonical /api/autonomous/repair is registered above.
    # Original implementation intentionally preserved.
    async def autonomous_repair_legacy():

        return tamanna_autonomous.repair()


    # LEGACY ROUTE DISABLED:
    # Linux Shell will later use the central controlled gateway.
    # Original implementation intentionally preserved.
    async def linux_shell_status_legacy():

        return {
            "online": True,
            "mode": "controlled",
            "root": str(
                tamanna_autonomous.root
            )
        }


    # LEGACY ROUTE DISABLED:
    # Linux Shell will later use the central controlled gateway.
    # Original implementation intentionally preserved.
    async def linux_shell_legacy(
        payload: dict
    ):

        return tamanna_autonomous.shell(
            payload.get(
                "command",
                ""
            )
        )


    print(
        "[TAMANNA AI] "
        "Autonomous Core: ONLINE"
    )

    print(
        "[TAMANNA AI] "
        "Startup Scan:",
        AUTONOMOUS_STARTUP[
            "project"
        ]["files"],
        "files"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] "
        "Autonomous Core ERROR:",
        exc
    )


# ============================================================
# TAMANNA AUTO MODULE CONNECTOR
# ============================================================

# AUTO CONNECTOR disabled during server startup.
# The full project scan was blocking Uvicorn from binding to port 8000.
TAMANNA_AUTO_CONNECTION_MAP = {
    "status": "disabled",
    "reason": "startup scan disabled to keep API responsive",
}
print("[AUTO CONNECTOR] DISABLED | startup scan skipped")


# ============================================================
# TAMANNA_MODULE_CONTROL_PLANE_V1
# ============================================================

try:
    from data.module_control.startup import startup_scan
    from data.module_control.api import router as module_control_router

    # Discover/analyze only.
    # Unknown modules are NOT automatically executed.
    # Startup scan disabled: it was blocking Uvicorn startup.
    # Module discovery can be triggered explicitly later.
    TAMANNA_MODULE_CONTROL_STATE = {
        "status": "disabled",
        "reason": "startup scan disabled to keep API responsive",
    }

    try:
        app.include_router(
            module_control_router
        )
    except Exception as route_exc:
        print(
            "[MODULE CONTROL] Router attach:",
            route_exc,
        )

    print(
        "[MODULE CONTROL] API ONLINE"
    )
    print(
        "[MODULE CONTROL] "
        "/api/module-control/status"
    )
    print(
        "[MODULE CONTROL] "
        "/api/module-control/scan"
    )
    print(
        "[MODULE CONTROL] "
        "/api/module-control/main"
    )
    print(
        "[MODULE CONTROL] "
        "/api/module-control/security"
    )

except Exception as exc:
    TAMANNA_MODULE_CONTROL_STATE = {
        "online": False,
        "error": str(exc),
    }

    print(
        "[MODULE CONTROL] FAILED:",
        exc,
    )

# ============================================================
# END TAMANNA_MODULE_CONTROL_PLANE_V1
# ============================================================



# ============================================================
# TAMANNA_MEMORY_SAFE_BRIDGE_V1
# ============================================================

def tamanna_normalize_memory_result(value):
    """
    Runtime guard for memory results.

    Prevents:
        AttributeError:
        'list' object has no attribute 'get'
    """

    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if isinstance(value, (list, tuple)):

        if not value:
            return None

        for item in value:
            if isinstance(item, dict):
                return item

        first = value[0]

        if isinstance(first, str):
            return {
                "reply": first,
                "text": first,
                "result": first,
            }

        return None

    if isinstance(value, str):
        return {
            "reply": value,
            "text": value,
            "result": value,
        }

    return None


def tamanna_memory_reply_from_result(value):
    """
    Safely extract a reply from memory.
    """

    data = tamanna_normalize_memory_result(value)

    if not data:
        return None

    for key in (
        "reply",
        "response",
        "answer",
        "text",
        "content",
        "message",
        "result",
    ):
        candidate = data.get(key)

        if isinstance(candidate, str):
            candidate = candidate.strip()

            if candidate:
                return candidate

    return None




# TAMANNA_SAFE_SYSTEM_UPGRADE_V1
# Additive integration — existing routes/functions are preserved.

try:
    from data.system_upgrade.startup import startup as tamanna_safe_upgrade_startup
    from data.system_upgrade.api import router as tamanna_safe_upgrade_router

    tamanna_safe_upgrade_startup()

    try:
        app.include_router(tamanna_safe_upgrade_router)
    except Exception as _tamanna_upgrade_router_error:
        print(
            "[SYSTEM UPGRADE] Router attach warning:",
            repr(_tamanna_upgrade_router_error),
        )

except Exception as _tamanna_upgrade_error:
    print(
        "[SYSTEM UPGRADE] Integration warning:",
        repr(_tamanna_upgrade_error),
    )

# END TAMANNA_SAFE_SYSTEM_UPGRADE_V1


# TAMANNA_FOUNDATION_V2
# Additive integration. Existing code/routes are preserved.

try:
    from data.foundation_v2.startup import startup as tamanna_foundation_startup
    from data.foundation_v2.api import router as tamanna_foundation_router

    tamanna_foundation_startup()

    try:
        app.include_router(
            tamanna_foundation_router
        )
    except Exception as _foundation_router_error:
        print(
            "[FOUNDATION V2] Router warning:",
            repr(_foundation_router_error),
        )

except Exception as _foundation_error:
    print(
        "[FOUNDATION V2] Integration warning:",
        repr(_foundation_error),
    )

# END TAMANNA_FOUNDATION_V2


# TAMANNA_CONTROLLER_V3
# Safe additive controller integration.

try:
    from data.tamanna_v3.controller import startup as tamanna_controller_v3_startup
    from data.tamanna_v3.api import router as tamanna_controller_v3_router

    tamanna_controller_v3_startup()

    try:
        app.include_router(
            tamanna_controller_v3_router
        )
    except Exception as _tamanna_v3_router_error:
        print(
            "[TAMANNA V3] Router warning:",
            repr(_tamanna_v3_router_error),
        )

except Exception as _tamanna_v3_error:
    print(
        "[TAMANNA V3] Integration warning:",
        repr(_tamanna_v3_error),
    )

# END TAMANNA_CONTROLLER_V3


# TAMANNA_MASTER_CONTROL_V1
# Central control plane.
# Existing functionality is preserved.

try:
    from data.master_control.startup import startup as tamanna_master_startup
    from data.master_control.api import router as tamanna_master_router

    tamanna_master_startup()

    try:
        app.include_router(
            tamanna_master_router
        )
    except Exception as _tamanna_master_router_error:
        print(
            "[TAMANNA MASTER] Router warning:",
            repr(_tamanna_master_router_error),
        )

except Exception as _tamanna_master_error:
    print(
        "[TAMANNA MASTER] Integration warning:",
        repr(_tamanna_master_error),
    )

# END TAMANNA_MASTER_CONTROL_V1

# ============================================================
# TAMANNA AI — CENTRAL COMMAND GATEWAY V1
# ============================================================

try:

    from data.action_router.action_executor import executor
    from data.linux.shell_bridge import shell_bridge

    def tamanna_command_handler(command="", timeout=15, **kwargs):
        """
        Central command handler.

        Uses the controlled LinuxShellBridge:
        - shlex parsing
        - allowlisted executables
        - subprocess(shell=False)
        - timeout
        """

        return shell_bridge.run(
            command,
            timeout=int(timeout),
        )


    # Register the existing controlled shell bridge with the
    # existing ActionExecutor.
    executor.register(
        "command",
        tamanna_command_handler,
    )


    @app.post("/api/command")
    async def tamanna_command(payload: dict):

        if not isinstance(payload, dict):
            return {
                "ok": False,
                "error": "JSON object required",
            }

        message = str(
            payload.get("message")
            or payload.get("command")
            or ""
        ).strip()

        command = str(
            payload.get("command")
            or ""
        ).strip()

        if not message:
            return {
                "ok": False,
                "error": "message or command required",
            }

        # ----------------------------------------------------
        # Preview mode
        # ----------------------------------------------------

        if payload.get("execute") is not True:

            from data.action_router.router_executor_bridge import (
                prepare_action,
            )

            preview = prepare_action(
                message,
                action="command",
                command=command,
                timeout=payload.get("timeout", 15),
            )

            return {
                "ok": True,
                "mode": "preview",
                "requires_confirmation": True,
                "preview": preview,
            }


        # ----------------------------------------------------
        # Real execution
        # ----------------------------------------------------

        confirmed = payload.get("confirm") is True

        if not confirmed:

            return {
                "ok": False,
                "status": "confirmation_required",
                "requires_confirmation": True,
                "message": (
                    "Command execution requires "
                    "confirm=true."
                ),
            }


        from data.action_router.router_executor_bridge import (
            execute_action,
        )

        result = execute_action(
            message,
            action="command",
            confirmed=True,
            dry_run=False,
            command=command,
            timeout=payload.get("timeout", 15),
        )

        return {
            "ok": result.status == "success",
            "request_id": result.request_id,
            "status": result.status,
            "intent": result.intent,
            "action": result.action,
            "message": result.message,
            "dry_run": result.dry_run,
            "timestamp": result.timestamp,
        }


    print(
        "[TAMANNA AI] Central Command Gateway: ONLINE"
    )

    print(
        "[TAMANNA AI] Command Handler: REGISTERED"
    )

    print(
        "[TAMANNA AI] POST /api/command"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Central Command Gateway ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END CENTRAL COMMAND GATEWAY V1
# ============================================================

# ============================================================
# TAMANNA AI — CONTROL CENTER V1
# Additive integration
# ============================================================

try:
    from data.control_center.api import router as tamanna_control_center_router

    app.include_router(
        tamanna_control_center_router
    )

    print(
        "[TAMANNA AI] Control Center V1: ONLINE"
    )

    print(
        "[TAMANNA AI] Permission Center: ONLINE"
    )

    print(
        "[TAMANNA AI] Project Intelligence: ONLINE"
    )

    print(
        "[TAMANNA AI] Audit Journal: ONLINE"
    )

    print(
        "[TAMANNA AI] Backup/Rollback: ONLINE"
    )

    print(
        "[TAMANNA AI] Git Control: ONLINE"
    )

    print(
        "[TAMANNA AI] Task Manager: ONLINE"
    )

    print(
        "[TAMANNA AI] System Monitor: ONLINE"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Control Center ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END CONTROL CENTER V1
# ============================================================

# ============================================================
# TAMANNA AI — CHAT CONTROL BRIDGE V1
# ============================================================

try:

    import json as tamanna_json
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    from data.control_center.core import (
        chat_command_bridge,
    )


    class TamannaChatControlMiddleware(
        BaseHTTPMiddleware
    ):
        """
        Intercepts only explicit Tamanna control commands.

        Example:

            tamanna find chat panel
            tamanna git-status
            tamanna scan
            tamanna backup

        Normal chat continues through the existing
        /api/chat pipeline.
        """

        async def dispatch(
            self,
            request,
            call_next,
        ):

            if (
                request.method.upper() != "POST"
                or request.url.path != "/api/chat"
            ):
                return await call_next(request)

            try:

                body = await request.body()

                if not body:
                    return await call_next(request)

                payload = tamanna_json.loads(
                    body.decode("utf-8")
                )

                if not isinstance(payload, dict):
                    return await call_next(request)

                message = str(
                    payload.get("message")
                    or payload.get("text")
                    or ""
                ).strip()

                if not chat_command_bridge.is_command(
                    message
                ):
                    return await call_next(request)

                result = chat_command_bridge.execute(
                    message,
                    confirmed=(
                        payload.get("confirm")
                        is True
                    ),
                )

                if not result.get("handled"):
                    return await call_next(request)

                # --------------------------------------------
                # Convert control result into Chat API format
                # --------------------------------------------

                intent = result.get(
                    "intent",
                    "control",
                )

                if (
                    result.get("status")
                    == "confirmation_required"
                ):

                    reply = (
                        "এই কাজটি করার জন্য তোমার "
                        "explicit confirmation প্রয়োজন।"
                    )

                elif intent == "find":

                    rows = result.get(
                        "results",
                        [],
                    )

                    if rows:

                        lines = [
                            "আমি project-এ এগুলো পেয়েছি:"
                        ]

                        for item in rows[:20]:

                            lines.append(
                                f"- {item.get('path')} "
                                f"(score={item.get('score', 0)})"
                            )

                        reply = "\n".join(lines)

                    else:

                        reply = (
                            "Project-এর মধ্যে matching "
                            "file পাওয়া যায়নি।"
                        )

                elif intent == "git_status":

                    data = result.get(
                        "result",
                        {},
                    )

                    if isinstance(data, dict):

                        stdout = data.get(
                            "stdout",
                            "",
                        )

                        stderr = data.get(
                            "stderr",
                            "",
                        )

                        reply = (
                            "Git status:\n"
                            + (
                                stdout
                                or stderr
                                or "No output"
                            )
                        )

                    else:
                        reply = str(data)

                elif intent == "scan":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "Project scan complete.\n"
                        f"Total files: "
                        f"{data.get('total_files', 0)}\n"
                        f"Python files: "
                        f"{data.get('python_files', 0)}\n"
                        f"Syntax errors: "
                        f"{data.get('syntax_errors', 0)}"
                    )

                elif intent == "backup":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "Backup created successfully.\n"
                        f"{data.get('archive', '')}"
                    )

                elif intent == "plan":

                    data = result.get(
                        "result",
                        {},
                    )

                    steps = data.get(
                        "steps",
                        [],
                    )

                    reply = (
                        "Plan created.\n"
                        f"Intent: "
                        f"{data.get('intent', '')}\n"
                        "Steps:\n"
                        + "\n".join(
                            f"{i + 1}. {step}"
                            for i, step in enumerate(steps)
                        )
                    )

                elif intent == "organize":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "Organization proposal তৈরি হয়েছে।\n"
                        "কোনো file এখনো move করা হয়নি।\n"
                        f"Candidates: "
                        f"{len(data.get('suggestions', []))}"
                    )

                elif intent == "status":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "Tamanna AI Control Center ONLINE.\n"
                        f"Version: "
                        f"{data.get('version', 'unknown')}\n"
                        f"Project: "
                        f"{data.get('project_root', '')}"
                    )

                elif intent == "system":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "System status:\n"
                        f"CPU: "
                        f"{data.get('cpu_percent', 'N/A')}%\n"
                        f"Memory: "
                        f"{data.get('memory_percent', 'N/A')}%\n"
                        f"Disk: "
                        f"{data.get('disk_percent', 'N/A')}%"
                    )

                elif intent == "permissions":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = (
                        "Permission Center ONLINE.\n"
                        f"Protected actions: "
                        f"{len(data.get('protected_actions', []))}"
                    )

                elif intent == "devices":

                    data = result.get(
                        "result",
                        {},
                    )

                    reply = str(
                        data.get(
                            "message",
                            "Device policy active."
                        )
                    )

                else:

                    reply = str(
                        result.get(
                            "result",
                            result.get(
                                "message",
                                "Control command completed.",
                            ),
                        )
                    )

                return JSONResponse(
                    {
                        "ok": bool(
                            result.get(
                                "ok",
                                False,
                            )
                        ),
                        "handled": True,
                        "source": "control_center",
                        "intent": intent,
                        "reply": reply,
                        "control_result": result,
                    }
                )

            except Exception as exc:

                # Do not break normal Chat API if the
                # control bridge itself has an error.

                print(
                    "[TAMANNA CONTROL CHAT] ERROR:",
                    type(exc).__name__,
                    exc,
                )

                return await call_next(request)


    app.add_middleware(
        TamannaChatControlMiddleware
    )

    print(
        "[TAMANNA AI] Chat → Control Center Bridge: ONLINE"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Chat Control Bridge ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END CHAT CONTROL BRIDGE V1
# ============================================================

# ============================================================
# ============================================================


# ============================================================
# UNIVERSAL ACTION PIPELINE
# ============================================================

try:
    from data.chat_action.universal_action_pipeline import (
        handle as universal_action_pipeline,
    )

    print(
        "[TAMANNA AI] Universal Action Pipeline: ONLINE"
    )

except Exception as exc:

    universal_action_pipeline = None

    print(
        "[TAMANNA AI] Universal Action Pipeline ERROR:",
        exc,
    )


@app.get("/health")
def health():
    return {"status": "ok"}

# ============================================================
# TAMANNA AI — ADVANCED CODE BUILDER V1
# ============================================================

try:
    from pathlib import Path

    from fastapi import Body

    from data.advanced_code_builder import (
        AdvancedCodeBuilder,
    )

    TAMANNA_PROJECT_ROOT = Path(__file__).resolve().parent

    tamanna_code_builder = AdvancedCodeBuilder(
        TAMANNA_PROJECT_ROOT
    )

    @app.get("/api/code-builder/status")
    async def code_builder_status():

        return {
            "ok": True,
            "service": "advanced_code_builder",
            "status": "online",
            "project_root": str(
                TAMANNA_PROJECT_ROOT
            ),
        }

    @app.get("/api/code-builder/project")
    async def code_builder_project():

        return tamanna_code_builder.discover()

    @app.post("/api/code-builder/plan")
    async def code_builder_plan(
        payload: dict = Body(...)
    ):

        request = str(
            payload.get("request")
            or payload.get("message")
            or ""
        )

        if not request.strip():
            return {
                "ok": False,
                "error": "request_required",
            }

        return {
            "ok": True,
            "plan": tamanna_code_builder.plan(
                request
            ),
        }

    @app.post("/api/code-builder/build")
    async def code_builder_build(
        payload: dict = Body(...)
    ):

        files = payload.get(
            "files",
            [],
        )

        overwrite = (
            payload.get("overwrite")
            is True
        )

        if not isinstance(files, list):
            return {
                "ok": False,
                "error": "files_must_be_list",
            }

        result = tamanna_code_builder.build(
            files=files,
            overwrite=overwrite,
        )

        return {
            "ok": result.ok,
            "language": result.language,
            "files": result.files,
            "checks": result.checks,
            "errors": result.errors,
            "warnings": result.warnings,
        }

    @app.post("/api/code-builder/compile")
    async def code_builder_compile():

        return tamanna_code_builder.python_compile_all()

    print(
        "[TAMANNA AI] Advanced Code Builder: ONLINE"
    )

except Exception as exc:

    print(
        "[TAMANNA AI] Advanced Code Builder ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END ADVANCED CODE BUILDER V1
# ============================================================



# ============================================================
# TAMANNA AI — UNIFIED SYSTEM V1
# ============================================================

try:
    from data.unified import unified_system

    unified_system.load(
        "Autonomous Brain",
        "data.autonomous.project_brain",
        "project_brain",
    )

    unified_system.load(
        "Autonomous Planner",
        "data.autonomous.planner",
        "autonomous_planner",
    )

    unified_system.load(
        "Safe Builder",
        "data.autonomous.builder",
        "safe_builder",
    )

    unified_system.load(
        "Chat Action Pipeline",
        "data.chat_action.universal_action_pipeline",
        "handle",
    )

    unified_system.load(
        "Control Center",
        "data.control_center.core",
        "chat_command_bridge",
    )

    @app.get("/api/unified/status")
    async def unified_status():
        return unified_system.health()

    @app.get("/api/unified/project")
    async def unified_project():
        return unified_system.discover()

    print("[TAMANNA AI] Unified System: ONLINE")

except Exception as exc:
    print(
        "[TAMANNA AI] Unified System ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END UNIFIED SYSTEM V1
# ============================================================

# ============================================================
# TAMANNA AI — CENTRAL AUTOMATION API BRIDGE V1
# STEP 31–35
# ============================================================

try:
    from data.central_automation.api_bridge import router as central_automation_router

    app.include_router(central_automation_router)

    print("[TAMANNA AI] Central Automation API Bridge: ONLINE")

except Exception as exc:
    print(
        "[TAMANNA AI] Central Automation API Bridge ERROR:",
        type(exc).__name__,
        exc,
    )

# ============================================================
# END CENTRAL AUTOMATION API BRIDGE
# ============================================================
