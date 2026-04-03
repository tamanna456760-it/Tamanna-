# akon_tamanna_sync.py
"""
Akon Code Auto-Sync & Build System for Tamanna AI
অকন কোড অটো সিঙ্ক এবং বিল্ড সিস্টেম
"""

import logging
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List

# Import Tamanna AI components
from tamanna_multilingual import TamannaMultilingual
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class AkonCodeMonitor:
    """Monitor Akon code files for changes and auto-sync with Tamanna AI"""

    def __init__(self, watch_dirs: List[str], build_dir: str = "./build"):
        self.watch_dirs = [Path(d).absolute() for d in watch_dirs]
        self.build_dir = Path(build_dir).absolute()
        self.tamanna_ai = TamannaMultilingual()
        self.observer = Observer()
        self.sync_queue = []
        self.is_monitoring = False

        # Setup directories
        self.build_dir.mkdir(exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(
                "akon_sync.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self):
        """Start monitoring Akon code files"""
        self.logger.info("Starting Akon Code Auto-Sync Monitor...")
        self.is_monitoring = True

        # Setup file system observer
        event_handler = AkonFileHandler(self)
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                self.observer.schedule(
                    event_handler, str(watch_dir), recursive=True)
                self.logger.info(f"Monitoring directory: {watch_dir}")

        self.observer.start()

        # Start sync processor thread
        sync_thread = threading.Thread(
            target=self._process_sync_queue, daemon=True)
        sync_thread.start()

        self.logger.info("Akon Code Auto-Sync started successfully!")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.observer.stop()
        self.observer.join()
        self.logger.info("Akon Code Auto-Sync stopped")

    def queue_sync(self, file_path: str, change_type: str):
        """Queue file for synchronization"""
        sync_item = {
            "file_path": file_path,
            "change_type": change_type,
            "timestamp": time.time(),
            "processed": False,
        }
        self.sync_queue.append(sync_item)
        self.logger.info(f"Queued for sync: {file_path} ({change_type})")

    def _process_sync_queue(self):
        """Process sync queue continuously"""
        while self.is_monitoring:
            if self.sync_queue:
                sync_item = self.sync_queue.pop(0)
                self._process_sync_item(sync_item)
            time.sleep(0.1)  # Small delay to prevent CPU overload

    def _process_sync_item(self, sync_item: Dict):
        """Process individual sync item"""
        try:
            file_path = Path(sync_item["file_path"])

            if file_path.suffix in [".akon", ".tmn", ".py", ".txt"]:
                # Sync with Tamanna AI
                self._sync_with_tamanna(file_path)

                # Auto-build if it's a buildable file
                if file_path.suffix in [".akon", ".tmn", ".py"]:
                    self._auto_build(file_path)

            sync_item["processed"] = True
            self.logger.info(f"Successfully processed: {file_path}")

        except Exception as e:
            self.logger.error(
                f"Error processing {sync_item['file_path']}: {e}")

    def _sync_with_tamanna(self, file_path: Path):
        """Sync file content with Tamanna AI"""
        try:
            if file_path.exists():
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Process with Tamanna AI based on file type
                if file_path.suffix == ".akon":
                    self._process_akon_code(content, file_path)
                elif file_path.suffix == ".tmn":
                    self._process_tamanna_code(content, file_path)
                else:
                    self._process_general_code(content, file_path)

        except Exception as e:
            self.logger.error(f"Tamanna AI sync error for {file_path}: {e}")

    def _process_akon_code(self, content: str, file_path: Path):
        """Process Akon specific code"""
        self.logger.info(f"Processing Akon code: {file_path.name}")

        # Convert Akon code to executable format
        executable_code = self._convert_akon_to_python(content)

        # Save converted code
        output_file = self.build_dir / f"{file_path.stem}_converted.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(executable_code)

        self.logger.info(f"Converted Akon code saved to: {output_file}")

    def _process_tamanna_code(self, content: str, file_path: Path):
        """Process Tamanna language code"""
        self.logger.info(f"Processing Tamanna code: {file_path.name}")

        # Execute Tamanna code directly
        output = self.tamanna_ai.execute(content)

        # Save execution results
        result_file = self.build_dir / f"{file_path.stem}_results.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            for line in output:
                f.write(line + "\n")

        self.logger.info(f"Tamanna execution results saved to: {result_file}")

    def _process_general_code(self, content: str, file_path: Path):
        """Process general code files"""
        self.logger.info(f"Processing general code: {file_path.name}")

        # Backup the file
        backup_file = self.build_dir / f"{file_path.name}.backup"
        shutil.copy2(file_path, backup_file)

    def _convert_akon_to_python(self, akon_code: str) -> str:
        """Convert Akon code to Python executable code"""
        # Simple conversion rules - extend as needed
        conversions = {
            "লেখো": "print",
            "নির্ধারণ": "",
            "যদি": "if",
            "নাহলে": "else",
            "যতক্ষণ": "while",
            "জন্য": "for",
            "কাজ": "def",
            "ফেরত": "return",
            "সত্য": "True",
            "মিথ্যা": "False",
        }

        python_code = akon_code
        for akon_key, python_key in conversions.items():
            python_code = python_code.replace(akon_key, python_key)

        # Add Python header
        python_code = f"# Converted from Akon code\n# Generated by Tamanna AI Auto-Sync\n\n{python_code}"

        return python_code

    def _auto_build(self, file_path: Path):
        """Auto-build the code file"""
        try:
            self.logger.info(f"Auto-building: {file_path}")

            if file_path.suffix == ".py":
                self._build_python(file_path)
            elif file_path.suffix == ".akon":
                self._build_akon(file_path)
            elif file_path.suffix == ".tmn":
                self._build_tamanna(file_path)

        except Exception as e:
            self.logger.error(f"Build error for {file_path}: {e}")

    def _build_python(self, file_path: Path):
        """Build Python code"""
        # Run Python file and capture output
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            cwd=file_path.parent,
        )

        # Save build results
        build_file = self.build_dir / f"{file_path.stem}_build.txt"
        with open(build_file, "w", encoding="utf-8") as f:
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"RETURN CODE: {result.returncode}\n")

        if result.returncode == 0:
            self.logger.info(f"Python build successful: {file_path}")
        else:
            self.logger.error(f"Python build failed: {file_path}")

    def _build_akon(self, file_path: Path):
        """Build Akon code"""
        # Convert and then build
        with open(file_path, "r", encoding="utf-8") as f:
            akon_code = f.read()

        python_code = self._convert_akon_to_python(akon_code)
        temp_python = self.build_dir / f"temp_{file_path.stem}.py"

        with open(temp_python, "w", encoding="utf-8") as f:
            f.write(python_code)

        self._build_python(temp_python)

    def _build_tamanna(self, file_path: Path):
        """Build Tamanna code"""
        with open(file_path, "r", encoding="utf-8") as f:
            tamanna_code = f.read()

        # Execute via Tamanna AI
        output = self.tamanna_ai.execute(tamanna_code)

        # Save build output
        build_file = self.build_dir / f"{file_path.stem}_tamanna_build.txt"
        with open(build_file, "w", encoding="utf-8") as f:
            f.write("Tamanna AI Execution Results:\n")
            for line in output:
                f.write(line + "\n")

        self.logger.info(f"Tamanna build completed: {file_path}")


class AkonFileHandler(FileSystemEventHandler):
    """File system event handler for Akon code"""

    def __init__(self, monitor: AkonCodeMonitor):
        self.monitor = monitor

    def on_modified(self, event):
        if not event.is_directory:
            self.monitor.queue_sync(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            self.monitor.queue_sync(event.src_path, "created")

    def on_deleted(self, event):
        if not event.is_directory:
            self.monitor.queue_sync(event.src_path, "deleted")

    def on_moved(self, event):
        if not event.is_directory:
            self.monitor.queue_sync(event.src_path, "moved")
            self.monitor.queue_sync(event.dest_path, "created")


class AkonBuildSystem:
    """Advanced build system for Akon code"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.cache_dir = self.project_root / ".akon_cache"

        # Setup directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - [AKON BUILD] - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def build_project(self):
        """Build entire Akon project"""
        self.logger.info("Starting Akon project build...")

        try:
            # Step 1: Find all Akon/Tamanna files
            akon_files = list(self.project_root.rglob("*.akon"))
            tmn_files = list(self.project_root.rglob("*.tmn"))
            py_files = list(self.project_root.rglob("*.py"))

            all_files = akon_files + tmn_files + py_files

            self.logger.info(f"Found {len(all_files)} buildable files")

            # Step 2: Process each file
            for file_path in all_files:
                self._build_file(file_path)

            # Step 3: Create package
            self._create_package()

            self.logger.info("Akon project build completed successfully!")

        except Exception as e:
            self.logger.error(f"Build failed: {e}")
            raise

    def _build_file(self, file_path: Path):
        """Build individual file"""
        self.logger.info(f"Building: {file_path}")

        if file_path.suffix == ".akon":
            self._build_akon_file(file_path)
        elif file_path.suffix == ".tmn":
            self._build_tamanna_file(file_path)
        elif file_path.suffix == ".py":
            self._build_python_file(file_path)

    def _build_akon_file(self, file_path: Path):
        """Build Akon file"""
        # Convert to Python
        with open(file_path, "r", encoding="utf-8") as f:
            akon_code = f.read()

        python_code = self._convert_akon_advanced(akon_code)

        # Save to build directory
        output_file = self.build_dir / f"{file_path.stem}.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(python_code)

        # Test the conversion
        try:
            exec(compile(python_code, str(output_file), "exec"))
            self.logger.info(f"Akon file built successfully: {file_path}")
        except Exception as e:
            self.logger.error(f"Akon build error: {e}")

    def _build_tamanna_file(self, file_path: Path):
        """Build Tamanna file"""
        tamanna_ai = TamannaMultilingual()

        with open(file_path, "r", encoding="utf-8") as f:
            tmn_code = f.read()

        # Execute and capture results
        output = tamanna_ai.execute(tmn_code)

        # Save results
        result_file = self.build_dir / f"{file_path.stem}_output.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("Tamanna Execution Results:\n")
            f.write("=" * 50 + "\n")
            for line in output:
                f.write(line + "\n")

        self.logger.info(f"Tamanna file processed: {file_path}")

    def _build_python_file(self, file_path: Path):
        """Build Python file"""
        # Simply copy to build directory
        build_file = self.build_dir / file_path.name
        shutil.copy2(file_path, build_file)
        self.logger.info(f"Python file copied: {file_path}")

    def _convert_akon_advanced(self, akon_code: str) -> str:
        """Advanced Akon to Python conversion"""
        # More sophisticated conversion rules
        conversions = {
            r'লেখো\s+"([^"]+)"': r'print("\1")',
            r"লেখো\s+([^;]+)": r"print(\1)",
            r"নির্ধারণ\s+(\w+)\s*=\s*([^;]+)": r"\1 = \2",
            r"যদি\s+([^:]+):": r"if \1:",
            r"নাহলে:": r"else:",
            r"যতক্ষণ\s+([^:]+):": r"while \1:",
            r"জন্য\s+(\w+)\s+মধ্যে\s+([^:]+):": r"for \1 in \2:",
            r"কাজ\s+(\w+)\(([^)]*)\):": r"def \1(\2):",
            r"ফেরত\s+([^;]+)": r"return \1",
            r"সত্য": "True",
            r"মিথ্যা": "False",
        }

        python_code = akon_code
        for pattern, replacement in conversions.items():
            python_code = re.sub(pattern, replacement, python_code)

        # Add Python imports and header
        header = '''"""
Generated from Akon code by Tamanna AI Build System
Automatically converted for execution
"""

import math
import os
import sys

'''

        return header + python_code

    def _create_package(self):
        """Create distributable package"""
        self.logger.info("Creating distribution package...")

        # Create requirements.txt
        requirements = ["watchdog", "pathlib", "typing"]

        req_file = self.dist_dir / "requirements.txt"
        with open(req_file, "w") as f:
            for req in requirements:
                f.write(req + "\n")

        # Create setup script
        setup_script = self._create_setup_script()
        setup_file = self.dist_dir / "setup.py"
        with open(setup_file, "w") as f:
            f.write(setup_script)

        self.logger.info("Distribution package created!")

    def _create_setup_script(self) -> str:
        """Create setup.py script"""
        return """
from setuptools import setup, find_packages

setup(
    name="akon-project",
    version="1.0.0",
    description="Akon code project built with Tamanna AI",
    packages=find_packages(),
    install_requires=[
        "watchdog",
        "pathlib",
        "typing"
    ],
    entry_points={
        "console_scripts": [
            "akon-run=main:main",
        ],
    },
)
"""


def create_sample_akon_files():
    """Create sample Akon code files for testing"""
    samples_dir = Path("./samples")
    samples_dir.mkdir(exist_ok=True)

    # Sample 1: Basic Akon code
    basic_akon = """
লেখো "আকন কোড থেকে স্বাগতম!"
নির্ধারণ নাম = "তামান্না AI"
নির্ধারণ বয়স = 25

লেখো "আমার নাম " + নাম + " এবং বয়স " + বয়স

যদি বয়স > 18:
    লেখো "আপনি প্রাপ্তবয়স্ক"
নাহলে:
    লেখো "আপনি নাবালক"
"""

    with open(samples_dir / "basic.akon", "w", encoding="utf-8") as f:
        f.write(basic_akon)

    # Sample 2: Mathematical Akon code
    math_akon = """
নির্ধারণ a = 10
নির্ধারণ b = 5

লেখো "যোগ: " + (a + b)
লেখো "বিয়োগ: " + (a - b)
লেখো "গুণ: " + (a * b)
লেখো "ভাগ: " + (a / b)

নির্ধারণ ব্যাসার্ধ = 7
নির্ধারণ ক্ষেত্রফল = 3.1416 * ব্যাসার্ধ * ব্যাসার্ধ
লেখো "বৃত্তের ক্ষেত্রফল: " + ক্ষেত্রফল
"""

    with open(samples_dir / "math.akon", "w", encoding="utf-8") as f:
        f.write(math_akon)

    # Sample 3: Tamanna language code
    tamanna_code = """
লেখো "তামান্না AI এ স্বাগতম!"
নির্ধারণ x = 15
নির্ধারণ y = 3

লেখো "x + y = " + (x + y)
লেখো "x * y = " + (x * y)

যদি x > y:
    লেখো "x বড়"
নাহলে:
    লেখো "y বড়"
"""

    with open(samples_dir / "demo.tmn", "w", encoding="utf-8") as f:
        f.write(tamanna_code)


def main():
    """Main function to run Akon Auto-Sync System"""
    print("Akon Code Auto-Sync & Build System for Tamanna AI")
    print("অকন কোড অটো সিঙ্ক এবং বিল্ড সিস্টেম\n")

    # Create sample files
    create_sample_akon_files()

    # Initialize monitor
    watch_dirs = ["./samples", "./src"]
    monitor = AkonCodeMonitor(watch_dirs)

    # Initialize build system
    build_system = AkonBuildSystem()

    try:
        # Build project once
        print("Building Akon project...")
        build_system.build_project()

        # Start auto-sync monitoring
        print("Starting auto-sync monitoring...")
        print("Monitoring directories:", watch_dirs)
        print("Press Ctrl+C to stop monitoring\n")

        monitor.start_monitoring()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping Akon Auto-Sync System...")
        monitor.stop_monitoring()
        print("System stopped successfully!")

    except Exception as e:
        print(f"System error: {e}")


if __name__ == "__main__":
    main()
