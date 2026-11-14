# Runner data build-output quarantine

Files below were moved out of `runner/data/` because their names and contents identify them as generated .NET/NuGet build metadata rather than runtime application data.

| Original path | Quarantine path | Original blob SHA |
|---|---|---|
| `runner/data/bd-king-agent.csproj.nuget.dgspec.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-agent.csproj.nuget.dgspec.json` | `0f0560d1dc2fa4e3c2a9617bd16f5dfaecc8663f` |
| `runner/data/bd-king-orchestrator.csproj.nuget.dgspec.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-orchestrator.csproj.nuget.dgspec.json` | `da5b5400f9dbe939c328a0862dd64b22758edcdc` |
| `runner/data/bd-king-orchestrator.deps.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-orchestrator.deps.json` | `7d1c73e3f0b15f152eb76dc9fc7f54f770d68728` |
| `runner/data/bd-king-orchestrator.runtimeconfig.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-orchestrator.runtimeconfig.json` | `ffac358f2bc53f457aa2ca8014aa4b528733322d` |
| `runner/data/bd-king-orchestrator.sourcelink.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-orchestrator.sourcelink.json` | `cc060fe441797519e0e9c16d8d1270537342b2df` |
| `runner/data/bd-king-website.csproj.nuget.dgspec.json` | `trash/quarantine-2026-11-15/runner-data-build-output/bd-king-website.csproj.nuget.dgspec.json` | `35b8dcb26572e6149ffd71e714fe91015acb8438` |
| `runner/data/project.assets.json` | `trash/quarantine-2026-11-15/runner-data-build-output/project.assets.json` | `ec1d7db8aafc424889fc329bf52bb0981b034f41` |
| `runner/data/staticwebassets.build.json` | `trash/quarantine-2026-11-15/runner-data-build-output/staticwebassets.build.json` | `ec05ca3bbd5427189dea946ecb46299d629c1d70` |

All file blobs are preserved unchanged. Restore by moving each file back to its original path if a verified workflow requires it.

## Malformed Python path repair

`runner/python/AI_CHAT\\chat_server.py` used a literal backslash in the filename. It was moved to `runner/python/AI_CHAT/chat_server.py` without changing its blob (`13345d63a6016274f4e344f973a6210294aca4d2`).