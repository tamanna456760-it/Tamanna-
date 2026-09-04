#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tamanna Auto-Save Daemon for BD-King-R7
Continuously monitors files and saves changes
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Set
import hashlib
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class AutoSaveDaemon(FileSystemEventHandler):
    """Daemon for automatic file saving"""
    
    def __init__(self, watch_dir: str = ".", config_file: str = "autosave_config.json"):
        self.watch_dir = Path(watch_dir)
        self.config = self.load_config(config_file)
        self.logger = self._setup_logging()
        self.file_hashes: Dict[str, str] = {}
        self.save_queue: Set[Path] = set()
        self.observer = None
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'watch_extensions': ['.py', '.js', '.json'],
                'autosave_interval': 5,
                'autosave_dir': '.autosave',
                'max_saves_per_file': 20,
                'log_level': 'INFO'
            }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        log_dir = self.watch_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger('AutoSaveDaemon')
        logger.setLevel(log_level)
        
        fh = logging.FileHandler(log_dir / 'autosave.log')
        ch = logging.StreamHandler()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if file should be watched
        if file_path.suffix not in self.config.get('watch_extensions', []):
            return
        
        # Add to save queue
        self.save_queue.add(file_path)
        self.logger.debug(f"File modified: {file_path}")
    
    def on_created(self, event):
        """Handle file creation"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix not in self.config.get('watch_extensions', []):
            return
        
        self.logger.info(f"New file: {file_path}")
    
    async def auto_save_loop(self):
        """Main auto-save loop"""
        while True:
            try:
                if self.save_queue:
                    self._process_save_queue()
                
                await asyncio.sleep(self.config.get('autosave_interval', 5))
            
            except Exception as e:
                self.logger.error(f"Error in auto-save loop: {e}")
    
    def _process_save_queue(self):
        """Process files in save queue"""
        for file_path in list(self.save_queue):
            try:
                if self._should_save(file_path):
                    self._save_file(file_path)
                    self.save_queue.remove(file_path)
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
    
    def _should_save(self, file_path: Path) -> bool:
        """Check if file should be saved"""
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'rb') as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
            
            previous_hash = self.file_hashes.get(str(file_path), '')
            
            if current_hash != previous_hash:
                self.file_hashes[str(file_path)] = current_hash
                return True
        except Exception as e:
            self.logger.error(f"Error checking file hash: {e}")
        
        return False
    
    def _save_file(self, file_path: Path):
        """Save file to autosave directory"""
        try:
            autosave_dir = self.watch_dir / self.config.get('autosave_dir', '.autosave')
            autosave_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = self.file_hashes.get(str(file_path), 'unknown')[:8]
            save_path = autosave_dir / f"{file_path.stem}_{timestamp}_{file_hash}{file_path.suffix}"
            
            with open(file_path, 'rb') as f:
                with open(save_path, 'wb') as s:
                    s.write(f.read())
            
            # Cleanup old saves
            self._cleanup_old_saves(file_path)
            
            self.logger.info(f"✓ Auto-saved: {save_path}")
        
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
    
    def _cleanup_old_saves(self, file_path: Path):
        """Remove old autosave files"""
        try:
            autosave_dir = self.watch_dir / self.config.get('autosave_dir', '.autosave')
            max_saves = self.config.get('max_saves_per_file', 20)
            
            # Find all saves for this file
            pattern = f"{file_path.stem}_*{file_path.suffix}"
            saves = sorted(autosave_dir.glob(pattern))
            
            # Remove oldest saves if exceeded max
            if len(saves) > max_saves:
                for old_save in saves[:-max_saves]:
                    old_save.unlink()
                    self.logger.debug(f"Cleaned up: {old_save}")
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def start(self):
        """Start daemon"""
        try:
            self.logger.info("🚀 Starting Auto-Save Daemon...")
            
            # Start watchdog observer
            self.observer = Observer()
            self.observer.schedule(self, str(self.watch_dir), recursive=True)
            self.observer.start()
            
            self.logger.info(f"✓ Watching: {self.watch_dir}")
        
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
    
    def stop(self):
        """Stop daemon"""
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            self.logger.info("✓ Auto-Save Daemon stopped")
        
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")


async def main():
    """Main entry point"""
    daemon = AutoSaveDaemon('bd-king-r7')
    daemon.start()
    
    try:
        # Run auto-save loop
        await daemon.auto_save_loop()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        daemon.stop()


if __name__ == '__main__':
    asyncio.run(main())
