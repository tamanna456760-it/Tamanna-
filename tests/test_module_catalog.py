from tamanna_ai.modules import ModuleRegistry, list_modules, load_builtin_modules


def test_builtin_modules_are_discoverable():
    registry = ModuleRegistry()
    load_builtin_modules(registry)
    names = registry.names()
    assert {"conversation", "coding", "file_management", "web_research",
            "weather", "finance", "image", "system", "research"} <= set(names)


def test_catalog_exposes_provider_and_approval_requirements():
    modules = {item["name"]: item for item in list_modules(ModuleRegistry())}
    assert modules["weather"]["provider_required"] is True
    assert modules["file_management"]["requires_approval"] is True
    assert modules["system"]["requires_approval"] is True
    assert modules["coding"]["status"] == "ready"


def test_load_builtin_modules_does_not_replace_custom_modules():
    registry = ModuleRegistry()
    custom = object()
    registry.register("coding", custom)
    load_builtin_modules(registry)
    assert registry.get("coding") is custom


def test_registry_rejects_empty_names():
    registry = ModuleRegistry()
    try:
        registry.register(" ", object())
    except ValueError:
        pass
    else:
        raise AssertionError("empty module names must be rejected")
