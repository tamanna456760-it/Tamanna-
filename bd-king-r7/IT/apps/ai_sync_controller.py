#!/usr/bin/env python3
import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


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
        print(f"📁 File changed: {file_path} - ai_sync_controller.py:27")

        # Run code analysis and fixing
        if self.config["code_fixing"]["auto_fix"]:
            self.analyze_and_fix_code(file_path)

        # Run tests if configured
        if self.config["code_fixing"]["test_before_sync"]:
            self.run_tests()

        # Auto commit if configured
        if self.config["git"]["auto_commit"]:
            self.auto_commit(file_path)


class AIAutoSync:
    def __init__(self, config_path="ai-sync-config.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        # Derived values
        self.interval = int(
            self.config.get("auto_sync", {}).get("interval_seconds", 60)
        )
        self._periodic_running = False

    def load_config(self, config_path):
        # Return defaults if config is missing or invalid
        defaults = {
            "auto_sync": {"watch_patterns": ["."], "interval_seconds": 60},
            "code_fixing": {"auto_fix": True, "test_before_sync": True},
            "git": {
                "auto_commit": False,
                "commit_message_template": "AutoFix: {timestamp} - {changes}",
            },
        }
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    # merge defaults with provided config (shallow)
                    merged = defaults.copy()
                    merged.update(cfg)
                    return merged
            else:
                logging.getLogger(__name__).warning(
                    f"Config {config_path} not found — using defaults"
                )
                return defaults
        except Exception as e:
            logging.getLogger(__name__).error(f"Error loading config: {e}")
            return defaults

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(
                "ai-sync.log"), logging.StreamHandler()],
        )

    def analyze_and_fix_code(self, file_path):
        """Analyze code and apply AI-powered fixes"""
        try:
            # Read the file content
            with open(file_path, "r") as f:
                content = f.read()

            # Prefer local automated fixes first (existing script)
            script = os.path.normpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "scripts",
                    "auto_build_and_fix.sh",
                )
            )
            if os.path.exists(script) and os.access(script, os.X_OK):
                logging.info(f"Running auto-fix script: {script}")
                try:
                    subprocess.run([script], check=False)
                except Exception as e:
                    logging.error(f"Error running auto-fix script: {e}")

            # Fallback to AI-based fixes (placeholder)
            fixed_content = self.get_ai_fixes(content, file_path)

            if fixed_content and fixed_content != content:
                with open(file_path, "w") as f:
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
                ["python", "-m", "pytest"],
                ["npm", "test"],
                ["./gradlew", "test"],
                ["mvn", "test"],
            ]

            for cmd in test_commands:
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True)
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
            subprocess.run(["git", "add", changed_file], check=True)

            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = self.config["git"]["commit_message_template"].format(
                timestamp=timestamp, changes=os.path.basename(changed_file)
            )

            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            logging.info(f"✅ Autocommitted: {commit_msg}")

        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Git commit failed: {str(e)}")

    def _run_periodic(self):
        """Run auto-fix periodically in the background."""
        self._periodic_running = True
        logging.info(
            f"⏱️ Starting periodic auto-fix every {self.interval} seconds")
        try:
            while self._periodic_running:
                # Run the script if enabled
                try:
                    script = os.path.normpath(
                        os.path.join(
                            os.path.dirname(__file__),
                            "..",
                            "..",
                            "scripts",
                            "auto_build_and_fix.sh",
                        )
                    )
                    if os.path.exists(script) and os.access(script, os.X_OK):
                        logging.info("Periodic: running auto-build-and-fix.sh")
                        subprocess.run([script], check=False)
                    else:
                        logging.debug(
                            "Periodic: auto fix script not found or not executable"
                        )
                except Exception as e:
                    logging.error(f"Error during periodic auto-fix: {e}")
                time.sleep(self.interval)
        except Exception:
            logging.exception("Periodic auto-fix loop exited unexpectedly")
        finally:
            self._periodic_running = False

    def start_watching(self):
        """Start the file system watcher"""
        event_handler = AIAutoSyncHandler(self.config)
        observer = Observer()

        watch_paths = self.config["auto_sync"]["watch_patterns"]
        for pattern in watch_paths:
            observer.schedule(event_handler, path=".", recursive=True)

        # Start periodic background runner
        periodic_thread = threading.Thread(
            target=self._run_periodic, daemon=True)
        periodic_thread.start()

        observer.start()
        logging.info("👀 AI AutoSync started watching for changes...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            # Stop periodic runner
            self._periodic_running = False

        observer.join()


if __name__ == "__main__":
    sync = AIAutoSync()
    sync.start_watching()
