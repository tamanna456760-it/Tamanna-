flowchart TD

subgraph group_automation["Automation loop"]
  node_ci["GitHub Actions<br/>orchestration<br/>[workflows]"]
  node_scripts["AI scripts<br/>repair tools<br/>[scripts]"]
  node_scanfix["Scan-fix loop<br/>python pipeline<br/>[scan.py]"]
  node_monitor["System monitor<br/>health monitor"]
  node_sync["Sync layer<br/>replication"]
end

subgraph group_core["AI core"]
  node_ai_core["AI brain<br/>decision engine<br/>[ai_brain_core.py]"]
  node_memory[("Memory store<br/>persistent state<br/>[brain_memory.json]")]
  node_learn["Learning<br/>adaptive logic<br/>[learning_system.py]"]
  node_modelcfg["Model config<br/>configuration"]
end

subgraph group_surfaces["Product surfaces"]
  node_api_py["Python API<br/>python service<br/>[main.py]"]
  node_ai_chat["Chat server<br/>chat service"]
  node_tamanna_sys["AI system<br/>python orchestrator<br/>[main.py]"]
  node_web_backend["Web backend<br/>node backend<br/>[server.js]"]
  node_web_frontend["Web frontend<br/>browser UI<br/>[main.jsx]"]
  node_dotnet_site[".NET site<br/>aspnet service<br/>[Program.cs]"]
  node_android_app["Android app<br/>kotlin client<br/>[MainActivity.kt]"]
end

subgraph group_security["Security"]
  node_security_core["Defense core<br/>security subsystem<br/>[security_system.py]"]
  node_server_defense["Server shield<br/>network defense<br/>[main.py]"]
end

subgraph group_infra["Infra + state"]
  node_readme["Repo map<br/>workspace overview<br/>[README.md]"]
  node_powerhub["Powerhub<br/>orchestration hub"]
  node_state_files[("Local state<br/>logs/db/json")]
end

node_readme -->|"documents"| node_ci
node_ci -->|"runs"| node_scripts
node_scripts -->|"drives"| node_scanfix
node_scripts -->|"checks"| node_monitor
node_scanfix -->|"writes"| node_state_files
node_monitor -->|"records"| node_state_files
node_sync -->|"triggered by"| node_ci
node_sync -->|"updates"| node_state_files
node_ai_core -->|"reads/writes"| node_memory
node_learn -->|"feeds"| node_ai_core
node_modelcfg -->|"configures"| node_ai_core
node_api_py -->|"uses"| node_ai_core
node_ai_chat -->|"fronts"| node_api_py
node_tamanna_sys -->|"wraps"| node_ai_core
node_web_backend -->|"serves"| node_api_py
node_web_frontend -->|"calls"| node_web_backend
node_dotnet_site -->|"stores"| node_state_files
node_android_app -->|"calls"| node_web_backend
node_android_app -->|"uses"| node_security_core
node_security_core -->|"logs"| node_state_files
node_server_defense -->|"extends"| node_security_core
node_powerhub -->|"coordinates"| node_sync
node_powerhub -->|"protects with"| node_server_defense
node_powerhub -->|"exposes"| node_web_frontend
node_powerhub -->|"persists"| node_state_files

click node_readme "https://github.com/tamanna456760-it/tamanna-/blob/main/README.md"
click node_ci "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows"
click node_scripts "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/scripts"
click node_scanfix "https://github.com/tamanna456760-it/tamanna-/blob/main/scripts/scan.py"
click node_monitor "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_system_monitor.py"
click node_sync "https://github.com/tamanna456760-it/tamanna-/blob/main/tamanna_distributed_system.py"
click node_ai_core "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_brain_core.py"
click node_memory "https://github.com/tamanna456760-it/tamanna-/blob/main/brain_memory.json"
click node_learn "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/core/learning_system.py"
click node_modelcfg "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/config"
click node_api_py "https://github.com/tamanna456760-it/tamanna-/blob/main/api/main.py"
click node_ai_chat "https://github.com/tamanna456760-it/tamanna-/blob/main/AI_CHAT\chat_server.py"
click node_tamanna_sys "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/main.py"
click node_web_backend "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/backend/server.js"
click node_web_frontend "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/frontend/src/main.jsx"
click node_dotnet_site "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/bd-king-website/Program.cs"
click node_android_app "https://github.com/tamanna456760-it/tamanna-/blob/main/tamanna-ai-app/app/src/main/java/com/tamanna/MainActivity.kt"
click node_security_core "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/potocol/Security/security_system.py"
click node_server_defense "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/potocol/server defanding potocol/main.py"
click node_powerhub "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/bd-king-r7/powerhub"
click node_state_files "https://github.com/tamanna456760-it/tamanna-/blob/main/ROOT/logs/tamanna_pro_cli.log"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_ci,node_scripts,node_scanfix,node_monitor,node_sync toneBlue
class node_ai_core,node_memory,node_learn,node_modelcfg toneAmber
class node_api_py,node_ai_chat,node_tamanna_sys,node_web_backend,node_web_frontend,node_dotnet_site,node_android_app toneMint
class node_security_core,node_server_defense toneRose
class node_readme,node_powerhub,node_state_files toneIndigo