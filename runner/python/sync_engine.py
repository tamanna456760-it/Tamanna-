# src/core/sync_engine.py
import asyncio
import hashlib
import logging
import os
import time
from typing import Dict

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class SyncEngine:
    """Core synchronization engine with real-time file monitoring"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.observer = Observer()
        self.event_handler = SyncEventHandler(self)
        self.sync_queues = {}
        self.last_sync_time = {}

        # Initialize sync queues for each environment
        for env in config.get("environments", {}).keys():
            self.sync_queues[env] = asyncio.Queue()

    async def start(self):
        """Start the sync engine"""
        self.logger.info("Starting Sync Engine...")

        # Setup file monitoring
        watch_paths = self.config["sync"]["watch_paths"]
        for path in watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.event_handler, path, recursive=True)
                self.logger.info(f"Monitoring path: {path}")

        self.observer.start()

        # Start sync processors for each environment
        sync_tasks = []
        for env in self.sync_queues.keys():
            task = asyncio.create_task(self._process_sync_queue(env))
            sync_tasks.append(task)

        self.logger.info("Sync Engine started successfully")
        return True

    def stop(self):
        """Stop the sync engine"""
        self.observer.stop()
        self.observer.join()
        self.logger.info("Sync Engine stopped")

    def queue_sync(self, file_path: str, change_type: str):
        """Queue a file for synchronization"""
        file_hash = self._calculate_file_hash(file_path)

        for env, queue in self.sync_queues.items():
            sync_item = {
                "file_path": file_path,
                "change_type": change_type,
                "file_hash": file_hash,
                "timestamp": time.time(),
                "environment": env,
            }
            asyncio.create_task(queue.put(sync_item))

    async def _process_sync_queue(self, environment: str):
        """Process sync queue for a specific environment"""
        while True:
            try:
                sync_item = await self.sync_queues[environment].get()
                await self._sync_file(sync_item)
                self.sync_queues[environment].task_done()
            except Exception as e:
                self.logger.error(f"Error processing sync queue for {environment}: {e}")

    async def _sync_file(self, sync_item: Dict):
        """Sync individual file to target environment"""
        try:
            file_path = sync_item["file_path"]
            environment = sync_item["environment"]

            env_config = self.config["environments"][environment]

            if env_config.get("auto_deploy", False):
                if await self._should_sync(file_path, environment):
                    await self._perform_sync(file_path, environment)
                    self.logger.info(f"Synced {file_path} to {environment}")

                    # Trigger build if configured
                    if self.config["build"].get("auto_build_on_sync", False):
                        asyncio.create_task(self._trigger_build(environment))

        except Exception as e:
            self.logger.error(f"Sync failed for {sync_item['file_path']}: {e}")

    async def _should_sync(self, file_path: str, environment: str) -> bool:
        """Determine if file should be synced based on rules"""
        # Check ignore patterns
        ignore_patterns = self.config["sync"]["ignore_patterns"]
        for pattern in ignore_patterns:
            if pattern in file_path:
                return False

        # Check rate limiting
        current_time = time.time()
        last_sync = self.last_sync_time.get(file_path, 0)
        sync_interval = self.config["sync"].get("sync_interval", 1.0)

        if current_time - last_sync < sync_interval:
            return False

        self.last_sync_time[file_path] = current_time
        return True

    async def _perform_sync(self, file_path: str, environment: str):
        """Perform actual file synchronization"""
        env_config = self.config["environments"][environment]

        if environment == "local":
            # Local sync - simple copy
            target_path = os.path.join(env_config["path"], file_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Use rsync for efficient sync if available
            if self._is_rsync_available():
                await self._rsync_file(file_path, target_path)
            else:
                import shutil

                shutil.copy2(file_path, target_path)

        else:
            # Remote sync using SSH/rsync
            await self._remote_sync(file_path, environment)

    async def _remote_sync(self, file_path: str, environment: str):
        """Sync file to remote environment"""
        env_config = self.config["environments"][environment]

        # Use rsync over SSH for efficient remote sync
        rsync_cmd = [
            "rsync",
            "-avz",
            "--progress",
            file_path,
            f"{env_config['username']}@{env_config['host']}:{env_config['path']}/",
        ]

        process = await asyncio.create_subprocess_exec(
            *rsync_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"RSync failed: {stderr.decode()}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash for change detection"""
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _is_rsync_available(self) -> bool:
        """Check if rsync is available on system"""
        try:
            import subprocess

            subprocess.run(["rsync", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    async def _trigger_build(self, environment: str):
        """Trigger build after sync"""
        # This would integrate with the BuildEngine
        self.logger.info(f"Triggering build for {environment}")


class SyncEventHandler(FileSystemEventHandler):
    """File system event handler for sync engine"""

    def __init__(self, sync_engine: SyncEngine):
        self.sync_engine = sync_engine
        self.logger = logging.getLogger(__name__)

    def on_modified(self, event):
        if not event.is_directory:
            self.sync_engine.queue_sync(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            self.sync_engine.queue_sync(event.src_path, "created")

    def on_deleted(self, event):
        if not event.is_directory:
            self.sync_engine.queue_sync(event.src_path, "deleted")

    def on_moved(self, event):
        if not event.is_directory:
            self.sync_engine.queue_sync(event.src_path, "moved")
            self.sync_engine.queue_sync(event.dest_path, "created")
