
Tamanna AI - Complete Interactive Kali Linux Manager
With Real-time Command Processing

class TamannaAI:
    def __init__(self):
        self.name = "Tamanna AI - Kali Linux Manager"
        self.version = "4.0"
        self.memory_file = "tamanna_memory.json"
        self.sync_enabled = True
        self.monitoring_enabled = False
        self.load_memory()
        
        # Initialize modules
        from kali_tools_manager import KaliToolsManager
        from auto_sync import AutoSyncManager
        from tool_executor import ToolExecutor
        from security_analyzer import SecurityAnalyzer
        
        self.tools_manager = KaliToolsManager()
        self.sync_manager = AutoSyncManager()
        self.tool_executor = ToolExecutor()
        self.security_analyzer = SecurityAnalyzer()
        
        # Command history
        self.command_history = []
        
        print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║ 🤖 {self.name} v{self.version}                          ║
    ║ 🚀 Autonomous Kali Linux Tools Management System            ║
    ║ 🔄 Auto-Sync: {'✅ ENABLED' if self.sync_enabled else '❌ DISABLED'}          ║
    ║ 👁️  Monitoring: {'✅ ACTIVE' if self.monitoring_enabled else '❌ INACTIVE'}         ║
    ╚══════════════════════════════════════════════════════════════╝
        """)
    
    def load_memory(self):
        """Load AI memory and configuration"""
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            self.memory = {
                "system_config": {
                    "auto_sync": True,
                    "backup_enabled": True,
                    "monitoring": False
                },
                "user_preferences": {},
                "tool_usage_stats": {},
                "sync_history": [],
                "security_scans": [],
                "command_history": []
            }
            self.save_memory()
    
    def save_memory(self):
        """Save AI memory"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def scan_command(self):
        """Execute security scan command"""
        print("🔍 Starting comprehensive security scan...")
        
        try:
            scan_results = self.security_analyzer.comprehensive_scan()
            
            # Display scan results
            print("\n" + "="*60)
            print("📊 SECURITY SCAN RESULTS")
            print("="*60)
            
            if "network_scan" in scan_results:
                print("\n🌐 NETWORK SCAN:")
                net_scan = scan_results["network_scan"]
                if "network_range" in net_scan:
                    print(f"   Network: {net_scan['network_range']}")
            
            if "system_services" in scan_results:
                print(f"\n🛠️  RUNNING SERVICES: {len(scan_results['system_services'])} services")
                for service in scan_results["system_services"][:5]:  # Show first 5
                    print(f"   • {service}")
            
            if "open_ports" in scan_results:
                print(f"\n🔓 OPEN PORTS: {len(scan_results['open_ports'])} ports")
                for port in scan_results["open_ports"][:5]:  # Show first 5
                    print(f"   • {port.get('local_address', 'N/A')}")
            
            if "firewall_status" in scan_results:
                print("\n🔥 FIREWALL STATUS:")
                fw = scan_results["firewall_status"]
                if "ufw" in fw and "Status: active" in fw["ufw"]:
                    print("   ✅ UFW Firewall: ACTIVE")
                else:
                    print("   ❌ UFW Firewall: INACTIVE")
            
            # Store in memory
            self.memory["security_scans"].append({
                "timestamp": datetime.now().isoformat(),
                "results": "scan_completed"
            })
            self.save_memory()
            
            print(f"\n✅ Security scan completed at {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
    
    def sync_command(self):
        """Execute sync command"""
        print("🔄 Starting synchronization process...")
        
        try:
            # Step 1: Update package lists
            print("📦 Step 1: Updating package lists...")
            result = subprocess.run(["sudo", "apt", "update"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Package lists updated")
            else:
                print("   ❌ Package update failed")
            
            # Step 2: Sync tool database
            print("🛠️  Step 2: Syncing tool database...")
            self.tools_manager.sync_tool_database()
            
            # Step 3: Backup configurations
            print("💾 Step 3: Backing up configurations...")
            self.sync_manager.backup_system_config()
            
            # Step 4: Update memory
            self.memory["sync_history"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "manual_sync",
                "status": "completed"
            })
            self.save_memory()
            
            print("✅ Synchronization completed successfully!")
            
        except Exception as e:
            print(f"❌ Synchronization failed: {e}")
    
    def tools_command(self):
        """List available tools"""
        print("\n🛠️  Available Kali Linux Tools")
        print("="*50)
        
        self.tools_manager.list_available_tools()
        
        # Show quick actions
        print("\n💡 Quick Actions:")
        print("   • 'execute <tool_name>' - Run a specific tool")
        print("   • 'install <tool_name>' - Install a missing tool")
        print("   • 'tools info <tool_name>' - Get detailed info")
    
    def execute_command(self, tool_name=None):
        """Execute specific tool"""
        if not tool_name:
            print("❌ Please specify a tool name")
            print("   Usage: execute <tool_name>")
            return
        
        print(f"🚀 Preparing to execute: {tool_name}")
        
        try:
            # Check if tool exists
            tool_info = self.tools_manager.get_tool_info(tool_name)
            if not tool_info:
                print(f"❌ Tool '{tool_name}' not found in database")
                return
            
            # Check if installed
            if not tool_info.get("installed", False):
                print(f"❌ {tool_name} is not installed")
                install = input("   Would you like to install it now? (y/n): ")
                if install.lower() == 'y':
                    if self.tools_manager.install_tool(tool_name):
                        print(f"✅ {tool_name} installed successfully!")
                    else:
                        return
                else:
                    return
            
            # Show available commands for the tool
            common_commands = tool_info.get("common_commands", [])
            if common_commands:
                print(f"\n🔧 Available commands for {tool_name}:")
                for i, cmd in enumerate(common_commands, 1):
                    print(f"   {i}. {cmd}")
                
                choice = input(f"\n   Choose command (1-{len(common_commands)}) or enter custom command: ")
                
                if choice.isdigit() and 1 <= int(choice) <= len(common_commands):
                    command = common_commands[int(choice) - 1]
                else:
                    command = choice
            else:
                command = input(f"   Enter command for {tool_name}: ")
            
            # Execute the tool
            success = self.tool_executor.execute_tool(tool_name, command)
            
            if success:
                # Update usage statistics
                if tool_name not in self.memory["tool_usage_stats"]:
                    self.memory["tool_usage_stats"][tool_name] = 0
                self.memory["tool_usage_stats"][tool_name] += 1
                self.save_memory()
                
        except Exception as e:
            print(f"❌ Execution failed: {e}")
    
    def health_command(self):
        """Check system health"""
        print("❤️  Checking system health...")
        
        try:
            health_data = self.check_system_health()
            
            print("\n" + "="*50)
            print("📊 SYSTEM HEALTH REPORT")
            print("="*50)
            
            # Disk usage
            print(f"\n💾 DISK USAGE:")
            disk_usage = psutil.disk_usage('/')
            print(f"   Total: {disk_usage.total // (1024**3)} GB")
            print(f"   Used: {disk_usage.used // (1024**3)} GB ({disk_usage.percent}%)")
            print(f"   Free: {disk_usage.free // (1024**3)} GB")
            
            # Memory usage
            print(f"\n🧠 MEMORY USAGE:")
            memory = psutil.virtual_memory()
            print(f"   Total: {memory.total // (1024**3)} GB")
            print(f"   Used: {memory.used // (1024**3)} GB ({memory.percent}%)")
            print(f"   Available: {memory.available // (1024**3)} GB")
            
            # CPU usage
            print(f"\n⚡ CPU USAGE:")
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   CPU Usage: {cpu_percent}%")
            print(f"   Cores: {psutil.cpu_count()} (Physical: {psutil.cpu_count(logical=False)})")
            
            # Network status
            print(f"\n🌐 NETWORK STATUS:")
            print(f"   Status: {health_data.get('network_status', 'Unknown')}")
            
            # Tools health
            print(f"\n🛠️  TOOLS HEALTH:")
            tools_health = health_data.get('tools_status', {})
            healthy_count = 0
            total_count = 0
            
            for category, tools in tools_health.items():
                for tool, status in tools.items():
                    total_count += 1
                    if status == "HEALTHY":
                        healthy_count += 1
            
            print(f"   Healthy: {healthy_count}/{total_count} tools")
            
            # Overall status
            print(f"\n📈 OVERALL STATUS:")
            if disk_usage.percent < 80 and memory.percent < 80 and cpu_percent < 80:
                print("   ✅ SYSTEM HEALTHY")
            else:
                print("   ⚠️  SYSTEM NEEDS ATTENTION")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def monitor_command(self):
        """Start/stop monitoring"""
        if not self.monitoring_enabled:
            print("👁️  Starting continuous monitoring...")
            self.monitoring_enabled = True
            self.start_monitoring()
            print("✅ Monitoring started! System will auto-sync every 5 minutes.")
        else:
            print("🛑 Stopping monitoring...")
            self.monitoring_enabled = False
            print("✅ Monitoring stopped.")
    
    def start_monitoring(self):
        """Start continuous system monitoring"""
        def monitor_loop():
            while self.monitoring_enabled:
                try:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[👁️ {current_time}] Monitoring check...")
                    
                    # Check system health
                    health = self.check_system_health()
                    
                    # Auto-sync if enabled
                    if self.sync_enabled:
                        self.auto_sync_tools()
                    
                    # Sleep for 5 minutes
                    for i in range(300):  # 5 minutes in seconds
                        if not self.monitoring_enabled:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def auto_sync_tools(self):
        """Automatically sync all Kali tools"""
        try:
            # Quick sync without extensive output
            subprocess.run(["sudo", "apt", "update"], 
                         capture_output=True, timeout=60)
            self.tools_manager.sync_tool_database()
            
        except Exception as e:
            print(f"Auto-sync warning: {e}")
    
    def check_system_health(self):
        """Check system health status"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "disk_usage": "Checked",
                "memory_usage": "Checked", 
                "network_status": self.check_network(),
                "tools_status": self.tools_manager.check_tools_health()
            }
            return health_status
        except Exception as e:
            return {"error": str(e)}
    
    def check_network(self):
        """Check network connectivity"""
        try:
            subprocess.run(["ping", "-c", "1", "8.8.8.8"], 
                         check=True, capture_output=True, timeout=5)
            return "Connected"
        except:
            return "Disconnected"
    
    def help_command(self):
        """Show help information"""
        print("""
🤖 TAMANNA AI COMMANDS HELP
═══════════════════════════════════════════════════

🔍 SECURITY & SCANNING:
   scan           - Run comprehensive security scan
   health         - Check system health status

🛠️  TOOLS MANAGEMENT:
   tools          - List all available Kali tools
   execute <tool> - Run specific tool (nmap, sqlmap, etc.)
   install <tool> - Install missing tool

🔄 SYSTEM & SYNC:
   sync           - Sync tools and system updates
   monitor        - Start/stop continuous monitoring
   status         - Show current system status

📊 INFORMATION:
   history        - Show command history
   stats          - Show usage statistics
   help           - Show this help message

🚪 EXIT:
   exit, quit     - Exit Tamanna AI

═══════════════════════════════════════════════════
💡 Tip: Use Tab for auto-completion
        """)
    
    def history_command(self):
        """Show command history"""
        print("\n📜 COMMAND HISTORY")
        print("="*40)
        
        if not self.command_history:
            print("No commands in history yet.")
            return
        
        for i, cmd in enumerate(self.command_history[-10:], 1):  # Last 10 commands
            print(f"  {i}. {cmd}")
    
    def stats_command(self):
        """Show usage statistics"""
        print("\n📊 USAGE STATISTICS")
        print("="*40)
        
        stats = self.memory.get("tool_usage_stats", {})
        if not stats:
            print("No usage statistics yet.")
            return
        
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        for tool, count in sorted_stats[:10]:  # Top 10 tools
            print(f"  {tool}: {count} executions")
    
    def status_command(self):
        """Show current system status"""
        print(f"""
🔄 SYSTEM STATUS
═══════════════════════════════════════════════════
🤖 AI System:      {self.name} v{self.version}
🔄 Auto-Sync:      {'✅ ENABLED' if self.sync_enabled else '❌ DISABLED'}
👁️  Monitoring:    {'✅ ACTIVE' if self.monitoring_enabled else '❌ INACTIVE'}
💾 Memory:         {len(self.memory.get('security_scans', []))} scans stored
🛠️  Tools:         {len(self.tools_manager.get_all_tools())} tools in database
📜 Commands:       {len(self.command_history)} in history
═══════════════════════════════════════════════════
        """)
    
    def auto_complete(self, text, state):
        """Auto-complete for commands"""
        commands = [
            'scan', 'sync', 'tools', 'execute', 'health', 'monitor',
            'help', 'history', 'stats', 'status', 'exit', 'quit',
            'install'
        ]
        matches = [cmd for cmd in commands if cmd.startswith(text.lower())]
        return matches[state] if state < len(matches) else None
    
    def interactive_mode(self):
        """Start interactive AI mode"""
        # Set up auto-completion
        readline.set_completer(self.auto_complete)
        readline.parse_and_bind("tab: complete")
        
        print(f"""
🎯 INTERACTIVE MODE ACTIVATED!
Type 'help' for available commands or 'exit' to quit.
        """)
        
        while True:
            try:
                command = input("\n🤖 Tamanna AI> ").strip()
                
                if not command:
                    continue
                
                # Add to history
                self.command_history.append(command)
                self.memory["command_history"] = self.command_history[-100:]  # Keep last 100
                self.save_memory()
                
                # Process command
                parts = command.lower().split()
                main_command = parts[0]
                
                if main_command in ['exit', 'quit']:
                    print("👋 Goodbye! Stay secure! 🛡️")
                    break
                
                elif main_command == "scan":
                    self.scan_command()
                
                elif main_command == "sync":
                    self.sync_command()
                
                elif main_command == "tools":
                    self.tools_command()
                
                elif main_command == "execute":
                    if len(parts) > 1:
                        self.execute_command(parts[1])
                    else:
                        print("❌ Please specify a tool name: execute <tool_name>")
                
                elif main_command == "health":
                    self.health_command()
                
                elif main_command == "monitor":
                    self.monitor_command()
                
                elif main_command == "help":
                    self.help_command()
                
                elif main_command == "history":
                    self.history_command()
                
                elif main_command == "stats":
                    self.stats_command()
                
                elif main_command == "status":
                    self.status_command()
                
                elif main_command == "install":
                    if len(parts) > 1:
                        self.tools_manager.install_tool(parts[1])
                    else:
                        print("❌ Please specify a tool name: install <tool_name>")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("   Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Stay secure! 🛡️")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    try:
        ai = TamannaAI()
        
        # Start auto-sync on launch
        print("🔄 Performing initial sync...")
        ai.sync_command()
        
        # Start interactive mode
        ai.interactive_mode()
        
    except Exception as e:
        print(f"❌ Failed to start Tamanna AI: {e}")
        sys.exit(1)