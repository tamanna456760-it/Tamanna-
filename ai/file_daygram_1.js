flowchart TD

subgraph group_grp_automation["Automation"]
  node_node_workflows["GitHub Actions<br/>CI orchestration<br/>[workflows]"]
  node_node_scripts["Helper Scripts<br/>automation tools<br/>[scripts]"]
  node_node_scan["Scan Loop<br/>repo scanner<br/>[scan.py]"]
  node_node_fix["Fix Loop<br/>auto-fixer<br/>[auto_fix_issues.py]"]
  node_node_sync["Sync Jobs<br/>sync scripts<br/>[auto_sync_all.sh]"]
end

subgraph group_grp_ai["AI Core"]
  node_node_ai_brain["AI Brain<br/>reasoning core<br/>[ai_brain_core.py]"]
  node_node_powerhub_core["Powerhub Core<br/>ai orchestration"]
  node_node_self_defense["Self Defense<br/>defense policy<br/>[ai_self_defense.py]"]
  node_node_integrity["Integrity Monitor<br/>code integrity"]
  node_node_network_defense["Network Defense<br/>network policy"]
  node_node_monitor["System Monitor<br/>runtime monitor"]
end

subgraph group_grp_services["Services"]
  node_node_node_backend["Node Backend<br/>API service<br/>[server.js]"]
  node_node_py_backend["Python Backend<br/>AI service<br/>[main.py]"]
  node_node_ts_api["API Server<br/>TypeScript API<br/>[app.ts]"]
  node_node_dotnet["Razor App<br/>.NET web app<br/>[Program.cs]"]
end

subgraph group_grp_clients["Clients"]
  node_node_android["Android App<br/>mobile control shell<br/>[MainActivity.kt]"]
  node_node_web_frontend["Web Frontend<br/>React/Vite UI<br/>[main.jsx]"]
  node_node_web_shells["Web Shells<br/>html/js ui<br/>[control_panel.html]"]
end

subgraph group_grp_state["State"]
  node_node_state[("State Files<br/>file-backed state<br/>[brain_memory.json]")]
  node_node_reports[("Reports DB<br/>sqlite state<br/>[projects.json]")]
end

subgraph group_grp_security["Security"]
  node_node_security["Security Stack<br/>defense subsystem"]
  node_node_protocols["Defense Protocols<br/>policy framework<br/>[main.py]"]
end

node_node_workflows -->|"triggers"| node_node_scan
node_node_workflows -->|"auto-heal"| node_node_fix
node_node_workflows -->|"sync"| node_node_sync
node_node_scripts -->|"analyze"| node_node_scan
node_node_scripts -->|"refactor"| node_node_fix
node_node_scan -->|"consults"| node_node_ai_brain
node_node_fix -->|"policy"| node_node_ai_brain
node_node_ai_brain -->|"enforces"| node_node_self_defense
node_node_ai_brain -->|"coordinates"| node_node_powerhub_core
node_node_powerhub_core -->|"observes"| node_node_monitor
node_node_integrity -->|"blocks"| node_node_self_defense
node_node_network_defense -->|"inspects"| node_node_security
node_node_node_backend -->|"stores"| node_node_state
node_node_py_backend -->|"uses"| node_node_ai_brain
node_node_ts_api -->|"persists"| node_node_state
node_node_dotnet -->|"reads"| node_node_reports
node_node_android -->|"calls"| node_node_node_backend
node_node_android -->|"syncs"| node_node_ts_api
node_node_web_frontend -->|"calls"| node_node_node_backend
node_node_web_shells -->|"hosts"| node_node_py_backend
node_node_security -->|"feeds"| node_node_protocols
node_node_protocols -->|"guards"| node_node_sync
node_node_monitor -->|"logs"| node_node_state

click node_node_workflows "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/workflows"
click node_node_scripts "https://github.com/tamanna456760-it/tamanna-/blob/main/.github/scripts"
click node_node_scan "https://github.com/tamanna456760-it/tamanna-/blob/main/scripts/scan.py"
click node_node_fix "https://github.com/tamanna456760-it/tamanna-/blob/main/auto_fix_issues.py"
click node_node_sync "https://github.com/tamanna456760-it/tamanna-/blob/main/auto_sync_all.sh"
click node_node_ai_brain "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_brain_core.py"
click node_node_powerhub_core "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_powerhub_core.py"
click node_node_self_defense "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_self_defense.py"
click node_node_integrity "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_code_integrity_monitor.py"
click node_node_network_defense "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_network_defense.py"
click node_node_monitor "https://github.com/tamanna456760-it/tamanna-/blob/main/ai_system_monitor.py"
click node_node_node_backend "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/server/backend/server.js"
click node_node_py_backend "https://github.com/tamanna456760-it/tamanna-/blob/main/Tamanna-AI-System/main.py"
click node_node_ts_api "https://github.com/tamanna456760-it/tamanna-/blob/main/artifacts/api-server/src/app.ts"
click node_node_dotnet "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/bd-king-website/Program.cs"
click node_node_android "https://github.com/tamanna456760-it/tamanna-/blob/main/tamanna-ai-app/app/src/main/java/com/tamanna/MainActivity.kt"
click node_node_web_frontend "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/frontend/src/main.jsx"
click node_node_web_shells "https://github.com/tamanna456760-it/tamanna-/blob/main/control_panel.html"
click node_node_state "https://github.com/tamanna456760-it/tamanna-/blob/main/brain_memory.json"
click node_node_reports "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/website/bd-king-website/data/projects.json"
click node_node_security "https://github.com/tamanna456760-it/tamanna-/blob/main/deep_packet_inspection.py"
click node_node_protocols "https://github.com/tamanna456760-it/tamanna-/blob/main/bd-king-r7/IT/potocol/server defanding potocol/main.py"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_node_workflows,node_node_scripts,node_node_scan,node_node_fix,node_node_sync toneBlue
class node_node_ai_brain,node_node_powerhub_core,node_node_self_defense,node_node_integrity,node_node_network_defense,node_node_monitor toneAmber
class node_node_node_backend,node_node_py_backend,node_node_ts_api,node_node_dotnet toneMint
class node_node_android,node_node_web_frontend,node_node_web_shells toneRose
class node_node_state,node_node_reports toneIndigo
class node_node_security,node_node_protocols toneTeal
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