"""Built-in Tamanna module catalog.

Modules are discoverable metadata entries. External integrations (weather,
currency rates, image generation, SMS delivery) remain disabled until a
provider is configured. Sensitive file/system actions require approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .registry import ModuleRegistry, module_registry


@dataclass(frozen=True)
class ModuleSpec:
    name: str
    title: str
    description: str
    actions: tuple[str, ...]
    status: str = "ready"
    requires_approval: bool = False
    provider_required: bool = False


BUILTIN_MODULES: tuple[ModuleSpec, ...] = (
    ModuleSpec("conversation", "Conversation & SMS", "Conversation support and SMS drafting; delivery requires an SMS provider.", ("chat", "draft_sms"), provider_required=True),
    ModuleSpec("coding", "Coding Assistant", "Code generation, explanation, review, debugging and refactoring.", ("generate", "explain", "review", "debug", "refactor")),
    ModuleSpec("file_management", "File Management", "Project file discovery and safe file-operation planning.", ("list", "search", "plan_create", "plan_edit", "plan_move"), requires_approval=True),
    ModuleSpec("web_research", "Web Search", "Search the web and collect source references when a provider is configured.", ("search", "collect_sources"), status="provider_required", provider_required=True),
    ModuleSpec("weather", "Weather", "Weather forecasts and current conditions through a configured weather provider.", ("current", "forecast"), status="provider_required", provider_required=True),
    ModuleSpec("finance", "Finance & Calculator", "Safe arithmetic is available locally; currency rates require a live data provider.", ("calculate", "currency_convert"), status="partial", provider_required=True),
    ModuleSpec("image", "Image", "Image understanding and generation through supported media providers.", ("analyze", "generate"), status="provider_required", provider_required=True),
    ModuleSpec("system", "System Tools", "Read-only system diagnostics; command execution is not exposed by this module.", ("health_check", "diagnostics"), requires_approval=True),
    ModuleSpec("research", "Research & Knowledge", "Organize research, retrieve project knowledge and prepare evidence-based summaries.", ("retrieve", "summarize", "cite")),
)


def load_builtin_modules(registry: ModuleRegistry = module_registry) -> ModuleRegistry:
    """Register built-in module specifications without replacing custom entries."""
    for spec in BUILTIN_MODULES:
        if registry.get(spec.name) is None:
            registry.register(spec.name, spec)
    return registry


def list_modules(registry: ModuleRegistry = module_registry) -> list[dict[str, Any]]:
    """Return serializable module metadata for dashboards and API responses."""
    load_builtin_modules(registry)
    return [
        {
            "name": spec.name,
            "title": spec.title,
            "description": spec.description,
            "actions": list(spec.actions),
            "status": spec.status,
            "requires_approval": spec.requires_approval,
            "provider_required": spec.provider_required,
        }
        for spec in registry.list()
        if isinstance(spec, ModuleSpec)
    ]


__all__ = ["ModuleSpec", "BUILTIN_MODULES", "load_builtin_modules", "list_modules"]
