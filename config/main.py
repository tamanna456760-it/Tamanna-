# main.py
#!/usr/bin/env python3
"""
Full System Auto-Sync & Auto-Build Main Controller
"""

import os
import sys
import signal
import logging
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.sync_engine import SyncEngine
from src.core.build_engine import BuildEngine
from src.core.monitoring_system import MonitoringSystem
from src.core.config_manager import ConfigManager
from src.utils.logger import setup_logging
from src.utils.health_check import HealthChecker

class AutoSyncBuildSystem:
    """Main system controller for auto-sync and auto-build functionality"""
    
    def __init__(self, config_path: str = "config/sync_config.yaml"):
        self.config_path = config_path
        self.config = None
        self.components = {}
        self.is_running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def initialize(self):
        """Initialize all system components"""
        try:
            # Load configuration
            self.config = ConfigManager.load_config(self.config_path)
            
            # Setup logging
            setup_logging(self.config.get('system', {}).get('log_level', 'INFO'))
            self.logger = logging.getLogger(__name__)
            
            # Initialize components
            self.components['sync'] = SyncEngine(self.config)
            self.components['build'] = BuildEngine(self.config)
            self.components['monitor'] = MonitoringSystem(self.config)
            self.components['health'] = HealthChecker(self.config)
            
            self.logger.info("Auto-Sync-Build system initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize system: {e}")
            return False
    
    async def start(self):
        """Start all system components"""
        if not self.initialize():
            return False
        
        self.is_running = True
        self.logger.info("Starting Auto-Sync-Build system...")
        
        try:
            # Start components
            startup_tasks = []
            for name, component in self.components.items():
                if hasattr(component, 'start'):
                    startup_tasks.append(component.start())
                    self.logger.info(f"Started {name} component")
            
            # Wait for all components to start
            await asyncio.gather(*startup_tasks)
            
            # Start health monitoring
            asyncio.create_task(self.components['health'].monitor_continuously())
            
            self.logger.info("All system components started successfully")
            
            # Keep system running
            while self.is_running:
                await asyncio.sleep(1)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error in system execution: {e}")
            return False
    
    def stop(self):
        """Stop all system components"""
        self.is_running = False
        self.logger.info("Stopping Auto-Sync-Build system...")
        
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                component.stop()
                self.logger.info(f"Stopped {name} component")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Auto-Sync-Build System')
    parser.add_argument('--config', default='config/sync_config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Set logging level')
    parser.add_argument('--dev', action='store_true', 
                       help='Run in development mode')
    
    args = parser.parse_args()
    
    # Set log level
    os.environ['LOG_LEVEL'] = args.log_level
    
    # Create system instance
    system = AutoSyncBuildSystem(args.config)
    
    # Run system
    try:
        asyncio.run(system.start())
    except KeyboardInterrupt:
        system.stop()
    except Exception as e:
        logging.error(f"System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()