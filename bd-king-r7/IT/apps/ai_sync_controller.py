#!/usr/bin/env python3
import os
import json
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from datetime import datetime

class AIAutoSyncHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.last_modified = time.time()
        self.debounce_seconds = 2
        
    def on_modified(self, event):
        if not event.is_directory:
            current_time = time.time()
            if current_time - self.last_modified > self.debounce_seconds:
                self.last_modified = current_time
                self.handle_file_change(event.src_path)
    
    def handle_file_change(self, file_path):
        print(f"📁 File changed: {file_path}")
        
        # Run code analysis and fixing
        if self.config['code_fixing']['auto_fix']:
            self.analyze_and_fix_code(file_path)
        
        # Run tests if configured
        if self.config['code_fixing']['test_before_sync']:
            self.run_tests()
        
        # Auto commit if configured
        if self.config['git']['auto_commit']:
            self.auto_commit(file_path)

class AIAutoSync:
    def __init__(self, config_path='ai-sync-config.json'):
        self.config = self.load_config(config_path)
        self.setup_logging()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai-sync.log'),
                logging.StreamHandler()
            ]
        )
    
    def analyze_and_fix_code(self, file_path):
        """Analyze code and apply AI-powered fixes"""
        try:
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Here you would integrate with AI API (OpenAI, etc.)
            fixed_content = self.get_ai_fixes(content, file_path)
            
            if fixed_content and fixed_content != content:
                with open(file_path, 'w') as f:
                    f.write(fixed_content)
                logging.info(f"✅ AI fixes applied to: {file_path}")
            
        except Exception as e:
            logging.error(f"❌ Error analyzing {file_path}: {str(e)}")
    
    def get_ai_fixes(self, content, file_path):
        """Get AI-powered code fixes (placeholder for AI integration)"""
        # This is where you'd integrate with OpenAI API, Claude, etc.
        # For now, return the original content
        return content
    
    def run_tests(self):
        """Run project tests"""
        try:
            # Try common test commands
            test_commands = [
                ['python', '-m', 'pytest'],
                ['npm', 'test'],
                ['./gradlew', 'test'],
                ['mvn', 'test']
            ]
            
            for cmd in test_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        logging.info("✅ Tests passed")
                        return True
                except FileNotFoundError:
                    continue
            
            logging.warning("⚠️ No tests found or tests failed")
            return False
            
        except Exception as e:
            logging.error(f"❌ Test execution error: {str(e)}")
            return False
    
    def auto_commit(self, changed_file):
        """Automatically commit changes to git"""
        try:
            # Stage the changed file
            subprocess.run(['git', 'add', changed_file], check=True)
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = self.config['git']['commit_message_template'].format(
                timestamp=timestamp,
                changes=os.path.basename(changed_file)
            )
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            logging.info(f"✅ Auto-committed: {commit_msg}")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Git commit failed: {str(e)}")
    
    def start_watching(self):
        """Start the file system watcher"""
        event_handler = AIAutoSyncHandler(self.config)
        observer = Observer()
        
        watch_paths = self.config['auto_sync']['watch_patterns']
        for pattern in watch_paths:
            observer.schedule(event_handler, path='.', recursive=True)
        
        observer.start()
        logging.info("👀 AI Auto-Sync started watching for changes...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()

if __name__ == "__main__":
    sync = AIAutoSync()
    sync.start_watching()