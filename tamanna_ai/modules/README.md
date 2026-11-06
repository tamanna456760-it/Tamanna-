# Tamanna AI built-in modules

The built-in module catalog is available from `tamanna_ai.modules`.

```python
from tamanna_ai.modules import list_modules, load_builtin_modules

load_builtin_modules()
for module in list_modules():
    print(module["name"], module["status"])
```

## Included modules

- Conversation & SMS (SMS delivery needs an SMS provider)
- Coding assistant
- File management (sensitive changes require approval)
- Web search and research (live search needs a configured provider)
- Weather (needs a weather provider)
- Finance and calculator (local safe arithmetic; live FX needs a provider)
- Image analysis and generation (needs a supported media provider)
- System diagnostics (read-only; no arbitrary shell execution)
- Research and knowledge retrieval

The catalog describes capabilities and integration requirements. It does not
pretend external providers are connected or execute sensitive actions.
