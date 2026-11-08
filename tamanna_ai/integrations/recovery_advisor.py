"""Read-only runtime recovery guidance for Tamanna AI local models."""
from __future__ import annotations

from typing import Any


def build_recovery_report(
    *,
    provider: str,
    selected_model: str | None,
    installed_models: list[str],
    runtime_error: str | None,
    host_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Classify common local inference failures without restarting or mutating services."""
    memory = host_metrics.get("memory", {}) if isinstance(host_metrics, dict) else {}
    disk = host_metrics.get("disk", {}) if isinstance(host_metrics, dict) else {}
    ram_usage = memory.get("usage_percent")
    disk_usage = disk.get("usage_percent")
    actions: list[str] = []

    if runtime_error == "provider_configuration":
        status, code = "attention", "provider_configuration"
        actions.append("TAMANNA_MODEL_PROVIDER এবং TAMANNA_OLLAMA_URL configuration যাচাই করুন।")
    elif runtime_error == "runtime_unreachable":
        status, code = "offline", "ollama_unreachable"
        actions.extend([
            "Ollama service চালু আছে কি না server-এ পরীক্ষা করুন।",
            "TAMANNA_OLLAMA_URL এবং local network/firewall settings যাচাই করুন।",
        ])
    elif runtime_error:
        status, code = "attention", "runtime_error"
        actions.append("Ollama log এবং runtime error পরীক্ষা করে service সুস্থ করুন।")
    elif provider != "ollama":
        status, code = "attention", "unsupported_provider"
        actions.append("Local model recovery diagnostics-এর জন্য Ollama provider নির্বাচন করুন।")
    elif not installed_models:
        status, code = "attention", "no_models_installed"
        actions.append("Ollama runtime-এ একটি model install করুন, তারপর status refresh করুন।")
    elif selected_model and selected_model not in installed_models:
        status, code = "attention", "selected_model_missing"
        actions.append("Installed model থেকে একটি model নির্বাচন করুন অথবা নির্বাচিত model install করুন।")
    else:
        status, code = "healthy", "runtime_available"
        actions.append("Local runtime ও selected model উপলভ্য। কোনো recovery action প্রয়োজন নেই।")

    if isinstance(ram_usage, (int, float)) and ram_usage >= 90:
        status = "attention"
        actions.append("RAM usage 90% বা বেশি; অন্য memory-heavy process বন্ধ করে আবার পরীক্ষা করুন।")
    elif isinstance(ram_usage, (int, float)) and ram_usage >= 80:
        actions.append("RAM usage বেশি; বড় context বা model চালানোর আগে free memory যাচাই করুন।")

    if isinstance(disk_usage, (int, float)) and disk_usage >= 95:
        status = "attention"
        actions.append("Disk প্রায় পূর্ণ; model download বা নতুন workload-এর আগে storage space খালি করুন।")
    elif isinstance(disk_usage, (int, float)) and disk_usage >= 85:
        actions.append("Disk space সীমিত; নতুন model download-এর আগে free storage যাচাই করুন।")

    return {
        "ok": True,
        "status": status,
        "code": code,
        "provider": provider,
        "selected_model": selected_model,
        "installed_model_count": len(installed_models),
        "actions": actions,
        "automatic_changes": False,
        "note": "এটি read-only diagnosis; service restart, model load, download বা configuration পরিবর্তন করে না।",
    }


__all__ = ["build_recovery_report"]
