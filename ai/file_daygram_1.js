flowchart TD

subgraph group_grp_control["Automation Loop"]
  node_scanner["Scanner<br/>analysis loop<br/>[scan.py]"]
  node_fixer["Fixer<br/>remediation loop<br/>[fixer.py]"]
  node_monitor["Monitor<br/>health loop<br/>[monitor.py]"]
  node_reporting["Reports<br/>feedback files<br/>[fix_report.json]"]
end

subgraph group_grp_orchestration["CI Control Plane"]
  node_gha["GitHub Actions<br/>orchestrator<br/>[workflows]"]
  node_gha_scripts["Workflow tools<br/>ops scripts<br/>[scripts]"]
  node_auto_run_wf["Auto run<br/>workflow<br/>[auto-run.yml]"]
  node_auto_heal_wf["Auto heal<br/>workflow<br/>[auto-heal.yml]"]
  node_auto_sync_wf["Auto sync<br/>workflow<br/>[auto-sync.yml]"]
end

subgraph group_grp_ai["AI Runtime"]
  node_tamanna_system["AI system<br/>python runtime<br/>[main.py]"]
  node_file_scanner["File scan<br/>python analyzer<br/>[file_scanner.py]"]
  node_ai_core["AI core<br/>decision engine<br/>[ai_brain_core.py]"]
  node_system_monitor_ai["System monitor<br/>runtime monitor"]
  node_learning["Learning<br/>adaptation engine<br/>[learning_system.py]"]
end

subgraph group_grp_security["Defense Boundary"]
  node_defense_core["Defense core<br/>security engine<br/>[ai_defense_core.py]"]
  node_net_defense["Net defense<br/>network security"]
  node_packet_inspection["Packet inspect<br/>traffic analysis"]
  node_self_defense["Self defense<br/>resilience layer<br/>[ai_self_defense.py]"]
end

subgraph group_grp_sync["Sync & Recovery"]
  node_sync_engine["Sync engine<br/>replication engine<br/>[git_sync.py]"]
  node_backup_mgr["Backup<br/>recovery manager<br/>[backup_manager.py]"]
  node_project_sync["Project sync<br/>sync monitor"]
end

subgraph group_grp_surfaces["User Surfaces"]
  node_bdking_web["Website<br/>web stack"]
  node_server_api["Server API<br/>node backend<br/>[server.js]"]
  node_android_app["Android app<br/>mobile client<br/>[MainActivity.kt]"]
  node_dashboard["Dashboard<br/>ui shell<br/>[index.html]"]
end

node_repo_root["Repo root<br/>umbrella monorepo"]
node_state_store["State files<br/>file storage<br/>[brain_memory.json]"]

node_repo_root -->|"source tree"| node_scanner
node_scanner -->|"findings"| node_reporting
node_reporting -->|"repair queue"| node_fixer
node_fixer -->|"verify"| node_monitor
node_monitor -->|"re-run"| node_scanner
node_gha -->|"triggers"| node_auto_run_wf
node_gha -->|"triggers"| node_auto_heal_wf
node_gha -->|"triggers"| node_auto_sync_wf
node_gha -->|"uses"| node_gha_scripts
node_gha_scripts -->|"invokes"| node_fixer
node_gha_scripts -->|"invokes"| node_scanner
node_tamanna_system -->|"analyzes"| node_file_scanner
node_file_scanner -->|"signals"| node_ai_core
node_ai_core -->|"updates"| node_learning
node_learning -->|"feedback"| node_system_monitor_ai
node_system_monitor_ai -->|"reports"| node_monitor
node_defense_core -->|"enforces"| node_net_defense
node_net_defense -->|"inspects"| node_packet_inspection
node_self_defense -->|"hardens"| node_defense_core
node_tamanna_system -->|"syncs"| node_sync_engine
node_sync_engine -->|"protects"| node_backup_mgr
node_project_sync -->|"monitors"| node_sync_engine
node_bdking_web -->|"serves"| node_server_api
node_android_app -->|"consumes"| node_bdking_web
node_dashboard -->|"controls"| node_server_api
node_state_store -->|"persists"| node_monitor
node_state_store -->|"persists"| node_ai_core
node_state_store -->|"replicates"| node_sync_engine

click node_scanner "https://github.com/tamanna456760-it/tamanna-/blob/main/scripts/scan.py"
click node_fixer "https://github.com/tamanna456760-it/tamanna-/blob/main/scripts/fixer.py"
click node_monitor "https://github.com/tamanna456760-it/tamanna-/blob/main/monitor.py"
click node_reporting "https://github.com/tamanna456760-it/tamanna-/blob/main/fix_report.json"
click node_gha "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows"
click node_gha_scripts "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/scripts"
click node_auto_run_wf "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows/auto-run.yml"
click node_auto_heal_wf "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows/auto-heal.yml"
click node_auto_sync_wf "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows/auto-sync.yml"
click node_tamanna_system "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/main.py"
click node_file_scanner "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/file_scanner.py"
click node_ai_core "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_brain_core.py"
click node_system_monitor_ai "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_system_monitor.py"
click node_learning "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/core/learning_system.py"
click node_defense_core "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_defense_core.py"
click node_net_defense "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_network_defense.py"
click node_packet_inspection "https://github.com/tamanna456760-it/tamanna-/blob/main/deep_packet_inspection.py"
click node_self_defense "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_self_defense.py"
click node_sync_engine "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/git_sync.py"
click node_backup_mgr "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/backup_manager.py"
click node_project_sync "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows/project_sync_monitor.py"
click node_bdking_web "https://github.com/tamanna456760-it/tamanna-/tree/main/bd-king-r7/website"
click node_server_api "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/server/server.js"
click node_android_app "https://github.com/tamanna456760-it/tamanna-/blob/main/tamanna-ai-app/app/src/main/java/com/tamanna/MainActivity.kt"
click node_dashboard "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/tamanna system/tamanna system-live dashbaord/index.html"
click node_state_store "https://github.com/tamanna456760-it/tamanna-/blob/main/brain_memory.json"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_scanner,node_fixer,node_monitor,node_reporting toneBlue
class node_gha,node_gha_scripts,node_auto_run_wf,node_auto_heal_wf,node_auto_sync_wf toneAmber
class node_tamanna_system,node_file_scanner,node_ai_core,node_system_monitor_ai,node_learning toneMint
class node_defense_core,node_net_defense,node_packet_inspection,node_self_defense toneRose
class node_sync_engine,node_backup_mgr,node_project_sync toneIndigo
class node_bdking_web,node_server_api,node_android_app,node_dashboard toneTeal
class node_repo_root,node_state_store toneNeutral

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