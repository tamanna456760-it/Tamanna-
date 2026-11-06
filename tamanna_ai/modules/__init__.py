"""Discoverable built-in modules for Tamanna AI."""

from .registry import ModuleRegistry, module_registry
from .catalog import BUILTIN_MODULES, ModuleSpec, list_modules, load_builtin_modules

__all__ = [
    "ModuleRegistry",
    "module_registry",
    "ModuleSpec",
    "BUILTIN_MODULES",
    "load_builtin_modules",
    "list_modules",
]
