"""Runtime capability layer for language, context, reasoning prompts and tools."""

from .assistant import CapabilityAssistant
from .prompt_engineering import build_code_generation_prompt, build_database_backend_prompt, build_debugging_prompt, build_documentation_prompt, build_project_documentation_prompt, build_refactoring_prompt, build_structured_prompt, supported_language_examples
from .tools import calculate, run_safe_tool
from .context_window import estimate_tokens, fit_context_window
from .web_search import BraveSearchClient, WebSearchError
from .web_fetch import SafeWebFetcher, WebFetchError

__all__ = ["CapabilityAssistant", "calculate", "run_safe_tool", "build_structured_prompt", "build_code_generation_prompt", "build_debugging_prompt", "build_documentation_prompt", "build_project_documentation_prompt", "build_database_backend_prompt", "build_refactoring_prompt", "supported_language_examples", "estimate_tokens", "fit_context_window", "BraveSearchClient", "WebSearchError", "SafeWebFetcher", "WebFetchError"]
