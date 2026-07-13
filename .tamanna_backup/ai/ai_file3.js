flowchart TD

subgraph group_g_control["Automation Control Plane"]
  node_n_readme_loop["Repo Loop<br/>automation loop<br/>[README.md]"]
  node_n_issue_scan["Issue Scan<br/>scanner"]
  node_n_auto_fix["Auto Fix<br/>repair engine<br/>[auto_fix_issues.py]"]
  node_n_monitor["Monitor<br/>[monitor.py]"]
  node_n_github_actions["GitHub Actions<br/>scheduler/control plane<br/>[workflows]"]
  node_n_github_scripts["Workflow Scripts<br/>automation helpers<br/>[scripts]"]
end

subgraph group_g_ai["AI Runtime"]
  node_n_python_ai["AI Core<br/>python reasoning<br/>[ai_brain_core.py]"]
  node_n_defense_core["Defense Core<br/>security AI<br/>[ai_defense_core.py]"]
  node_n_sys_monitor["AI Monitor<br/>observability"]
  node_n_tamanna_ai_system["AI System<br/>python package<br/>[main.py]"]
end

subgraph group_g_platforms["Product Surfaces"]
  node_n_artifacts_api["API Server<br/>node api<br/>[app.ts]"]
  node_n_artifacts_db[("DB Schema<br/>data schema<br/>[index.ts]")]
  node_n_website_stack["Website Stack<br/>multi-runtime web<br/>[Program.cs]"]
  node_n_server_stack["Server Stack<br/>node web backend<br/>[server.js]"]
  node_n_mobile_app["Android App<br/>kotlin mobile<br/>[MainActivity.kt]"]
end

subgraph group_g_powerhub["Powerhub Platform"]
  node_n_powerhub_root["Powerhub Root<br/>platform subsystem"]
  node_n_powerhub_orch["Orchestrator<br/>[program.cs]"]
  node_n_powerhub_agent["Agent<br/>[program.cs]"]
end

subgraph group_g_state["Shared State"]
  node_n_state_reports["Reports<br/>file state<br/>[issues_report.json]"]
  node_n_state_logs["Logs<br/>file state<br/>[run.log]"]
  node_n_state_configs["Configs<br/>file state"]
  node_n_state_contracts["Contracts<br/>api contract<br/>[openapi.yaml]"]
end

node_n_github_actions -->|"schedule"| node_n_issue_scan
node_n_github_actions -->|"run fixes"| node_n_auto_fix
node_n_github_actions -->|"health checks"| node_n_monitor
node_n_github_actions -->|"invoke"| node_n_github_scripts
node_n_readme_loop -->|"starts with"| node_n_issue_scan
node_n_issue_scan -->|"writes"| node_n_state_reports
node_n_auto_fix -->|"updates"| node_n_state_reports
node_n_monitor -->|"appends"| node_n_state_logs
node_n_github_scripts -->|"reads/writes"| node_n_state_configs
node_n_python_ai -->|"reads"| node_n_state_configs
node_n_python_ai -->|"writes"| node_n_state_logs
node_n_defense_core -->|"writes"| node_n_state_logs
node_n_sys_monitor -->|"writes"| node_n_state_logs
node_n_python_ai -->|"feeds"| node_n_defense_core
node_n_python_ai -->|"feeds"| node_n_sys_monitor
node_n_tamanna_ai_system -->|"packages"| node_n_python_ai
node_n_tamanna_ai_system -->|"loads"| node_n_state_configs
node_n_artifacts_api -->|"persists"| node_n_artifacts_db
node_n_artifacts_api -->|"implements"| node_n_state_contracts
node_n_website_stack -->|"consumes"| node_n_artifacts_api
node_n_server_stack -->|"consumes"| node_n_artifacts_api
node_n_mobile_app -->|"calls"| node_n_artifacts_api
node_n_mobile_app -->|"syncs"| node_n_state_configs
node_n_powerhub_root -->|"contains"| node_n_powerhub_orch
node_n_powerhub_orch -->|"dispatches"| node_n_powerhub_agent
node_n_powerhub_root -->|"records"| node_n_state_logs
node_n_powerhub_root -->|"uses"| node_n_state_configs
node_n_powerhub_root -.->|"shares patterns"| node_n_defense_core
node_n_github_actions -->|"sync/deploy"| node_n_powerhub_root

click node_n_readme_loop "https://github.com/tamanna456760-it/tamanna-/blob/main/README.md"
click node_n_issue_scan "https://github.com/tamanna456760-it/tamanna-/blob/main/lint_and_detect_issues.py"
click node_n_auto_fix "https://github.com/tamanna456760-it/tamanna-/blob/main/auto_fix_issues.py"
click node_n_monitor "https://github.com/tamanna456760-it/tamanna-/blob/main/monitor.py"
click node_n_github_actions "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows"
click node_n_github_scripts "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/scripts"
click node_n_python_ai "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_brain_core.py"
click node_n_defense_core "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_defense_core.py"
click node_n_sys_monitor "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_system_monitor.py"
click node_n_tamanna_ai_system "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/main.py"
click node_n_artifacts_api "https://github.com/tamanna456760-it/tamanna-/blob/main/artifacts/api-server/src/app.ts"
click node_n_artifacts_db "https://github.com/tamanna456760-it/tamanna-/blob/main/artifacts/lib/db/src/schema/index.ts"
click node_n_website_stack "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/bd-king-website/Program.cs"
click node_n_server_stack "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/server/server.js"
click node_n_mobile_app "https://github.com/tamanna456760-it/tamanna-/blob/main/tamanna-ai-app/app/src/main/java/com/tamanna/MainActivity.kt"
click node_n_powerhub_root "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/IT/bd-king-r7/powerhub"
click node_n_powerhub_orch "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/bd-king-r7/powerhub/bd-king-r7 powerhub/orchestrator/program.cs"
click node_n_powerhub_agent "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/bd-king-r7/powerhub/bd-king-r7 powerhub/orchestrator/agent/program.cs"
click node_n_state_reports "https://github.com/tamanna456760-it/tamanna-/blob/main/issues_report.json"
click node_n_state_logs "https://github.com/tamanna456760-it/tamanna-/blob/main/logs/run.log"
click node_n_state_configs "https://github.com/tamanna456760-it/tamanna-/blob/main/ai-sync-config.json"
click node_n_state_contracts "https://github.com/tamanna456760-it/tamanna-/blob/main/artifacts/lib/api-spec/openapi.yaml"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_n_readme_loop,node_n_issue_scan,node_n_auto_fix,node_n_monitor,node_n_github_actions,node_n_github_scripts toneBlue
class node_n_python_ai,node_n_defense_core,node_n_sys_monitor,node_n_tamanna_ai_system toneAmber
class node_n_artifacts_api,node_n_artifacts_db,node_n_website_stack,node_n_server_stack,node_n_mobile_app toneMint
class node_n_powerhub_root,node_n_powerhub_orch,node_n_powerhub_agent toneRose
class node_n_state_reports,node_n_state_logs,node_n_state_configs,node_n_state_contracts toneIndigo