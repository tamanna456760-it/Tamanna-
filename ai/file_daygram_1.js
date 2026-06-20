flowchart TD

subgraph group_grp_root["Root control plane"]
  node_n_root_cli["CLI runners<br/>entrypoints"]
  node_n_root_cfg["Build config<br/>toolchain"]
  node_n_bootstrap["Boot/runtime<br/>deployment runtime"]
end

subgraph group_grp_gha["GitHub automation"]
  node_n_gha_workflows["Workflows<br/>ci automation<br/>[workflows]"]
  node_n_gha_scripts["Action helpers<br/>ci helpers<br/>[scripts]"]
end

subgraph group_grp_ai["AI repair loop"]
  node_n_scan["Issue scan<br/>analysis"]
  node_n_fix["Auto fixer<br/>repair<br/>[auto_fix_issues.py]"]
  node_n_watch["Health watch<br/>monitoring<br/>[monitor.py]"]
end

subgraph group_grp_bdking["BD-KING-R7 suite"]
  node_n_bd_powerhub["Powerhub<br/>orchestrator suite"]
  node_n_bd_sync["Sync stack<br/>sync pipeline"]
  node_n_bd_security{{"Defense core<br/>security subsystem"}}
  node_n_bd_data["Data models<br/>analytics and ML"]
end

subgraph group_grp_tamanna["Tamanna systems"]
  node_n_ai_system["Tamanna AI<br/>python service<br/>[main.py]"]
  node_n_ai_brain["AI core<br/>decision layer<br/>[ai_brain_core.py]"]
  node_n_tamanna_system["Tamanna system<br/>service family"]
end

subgraph group_grp_web["Web surfaces"]
  node_n_bd_server["Server stack<br/>web backend"]
  node_n_website["Website stack<br/>multi-runtime web"]
end

subgraph group_grp_mobile["Mobile/device"]
  node_n_mobile_app["Android app<br/>mobile client"]
  node_n_bd_android["BD Android<br/>mobile integration"]
end

subgraph group_grp_state["State and logs"]
  node_n_state[("State files<br/>persistent state")]
end

node_n_root_cli -->|"run scan"| node_n_scan
node_n_root_cli -->|"run repair"| node_n_fix
node_n_root_cli -->|"run monitor"| node_n_watch
node_n_root_cfg -->|"drive"| node_n_root_cli
node_n_scan -->|"find issues"| node_n_fix
node_n_fix -->|"verify health"| node_n_watch
node_n_gha_workflows -->|"invoke helpers"| node_n_gha_scripts
node_n_gha_workflows -->|"dispatch jobs"| node_n_root_cli
node_n_gha_workflows -->|"lint and scan"| node_n_scan
node_n_gha_workflows -->|"auto-heal"| node_n_fix
node_n_ai_system -->|"persist state"| node_n_state
node_n_ai_brain -->|"observe"| node_n_watch
node_n_ai_brain -->|"decide repairs"| node_n_fix
node_n_bd_powerhub -->|"sync"| node_n_bd_sync
node_n_bd_powerhub -->|"defend"| node_n_bd_security
node_n_bd_powerhub -->|"learn from data"| node_n_bd_data
node_n_bd_sync -->|"write reports"| node_n_state
node_n_bd_security -->|"log events"| node_n_state
node_n_bd_server -->|"serve UI"| node_n_website
node_n_bd_server -->|"store data"| node_n_state
node_n_website -->|"read/write"| node_n_state
node_n_tamanna_system -->|"persist memory"| node_n_state
node_n_mobile_app -->|"call APIs"| node_n_bd_server
node_n_bd_android -->|"bridge control"| node_n_bd_powerhub
node_n_bootstrap -->|"launch"| node_n_root_cli
node_n_bootstrap -->|"deploy"| node_n_bd_powerhub

click node_n_scan "https://github.com/tamanna456760-it/tamanna-/blob/main/lint_and_detect_issues.py"
click node_n_fix "https://github.com/tamanna456760-it/tamanna-/blob/main/auto_fix_issues.py"
click node_n_watch "https://github.com/tamanna456760-it/tamanna-/blob/main/monitor.py"
click node_n_gha_workflows "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows"
click node_n_gha_scripts "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/scripts"
click node_n_ai_system "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/main.py"
click node_n_ai_brain "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_brain_core.py"
click node_n_bd_powerhub "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/bd-king-r7/powerhub"
click node_n_bd_sync "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/bd-king-r7/sync"
click node_n_bd_security "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/potocol"
click node_n_bd_data "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/data"
click node_n_bd_server "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/server"
click node_n_website "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/website"
click node_n_tamanna_system "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/tamanna system"
click node_n_mobile_app "https://github.com/tamanna456760-it/tamanna-/tree/main/tamanna-ai-app"
click node_n_bd_android "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/tamannna-android"
click node_n_bootstrap "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/boot"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_n_root_cli,node_n_root_cfg,node_n_bootstrap,node_n_mobile_app,node_n_bd_android toneBlue
class node_n_gha_workflows,node_n_gha_scripts,node_n_state toneAmber
class node_n_scan,node_n_fix,node_n_watch toneMint
class node_n_bd_powerhub,node_n_bd_sync,node_n_bd_security,node_n_bd_data toneRose
class node_n_ai_system,node_n_ai_brain,node_n_tamanna_system toneIndigo
class node_n_bd_server,node_n_website toneTeal