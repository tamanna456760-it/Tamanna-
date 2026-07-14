#!/usr/bin/env python3
"""
BD-King-R7 Auto Code Fixer and Synchronization System
"""

import ast
import hashlib
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class CodeAnalyzer:
    """Advanced code analysis and quality assessment"""

    def __init__(self, config_path: str = "builder.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning("Config file not found, using defaults")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "auto_fix": True,
            "auto_sync": True,
            "code_quality_threshold": 80,
            "file_patterns": {
                "include": ["**/*.py", "**/*.js", "**/*.html", "**/*.css"],
                "exclude": ["node_modules/**", "venv/**", ".git/**"],
            },
        }

    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("code_fixer.log"), logging.StreamHandler()],
        )

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for issues"""
        issues = []
        suggestions = []
        file_hash = self.get_file_hash(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_ext = Path(file_path).suffix.lower()

            # Language-specific analysis
            if file_ext == ".py":
                issues.extend(self.analyze_python(content, file_path))
            elif file_ext == ".js":
                issues.extend(self.analyze_javascript(content, file_path))
            elif file_ext in [".html", ".css"]:
                issues.extend(self.analyze_web_files(content, file_path))

            # General code quality checks
            issues.extend(self.general_quality_checks(content, file_path))

            # Generate suggestions
            suggestions = self.generate_suggestions(issues, file_path)

        except Exception as e:
            logging.error(f"Error analyzing {file_path}: {e}")
            issues.append({"type": "error", "message": f"Analysis failed: {e}"})

        return {
            "file_path": file_path,
            "file_hash": file_hash,
            "issues": issues,
            "suggestions": suggestions,
            "analysis_time": datetime.now().isoformat(),
        }

    def analyze_python(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Python code for issues"""
        issues = []

        try:
            # Parse AST for deeper analysis
            tree = ast.parse(content)

            # Check for common issues
            issues.extend(self.check_python_syntax(tree, file_path))
            issues.extend(self.check_unused_imports(tree, file_path))
            issues.extend(self.check_code_complexity(content, file_path))

        except SyntaxError as e:
            issues.append(
                {
                    "type": "error",
                    "message": f"Syntax error: {e}",
                    "line": e.lineno,
                    "fixable": True,
                }
            )

        return issues

    def analyze_javascript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript code for issues"""
        issues = []

        # Check for common JS issues
        if "console.log" in content and "test" not in file_path:
            issues.append(
                {
                    "type": "warning",
                    "message": "Found console.log statements in production code",
                    "fixable": True,
                }
            )

        # Check for missing semicolons
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if (
                line
                and not line.startswith("//")
                and not line.endswith(";")
                and not line.endswith("{")
            ):
                if not any(x in line for x in ["if", "for", "while", "function", "=>"]):
                    issues.append(
                        {
                            "type": "warning",
                            "message": f"Missing semicolon at line {i}",
                            "line": i,
                            "fixable": True,
                        }
                    )

        return issues

    def analyze_web_files(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze HTML/CSS files"""
        issues = []
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".html":
            # Check HTML issues
            if "<br>" in content and "<br />" not in content:
                issues.append(
                    {
                        "type": "warning",
                        "message": "Use self-closing tags for better compatibility",
                        "fixable": True,
                    }
                )

        elif file_ext == ".css":
            # Check CSS issues
            if "!important" in content:
                issues.append(
                    {
                        "type": "warning",
                        "message": "Avoid using !important, refactor CSS specificity",
                        "fixable": False,
                    }
                )

        return issues

    def general_quality_checks(
        self, content: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """General code quality checks for all file types"""
        issues = []

        # Check line length
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 100:  # Configurable
                issues.append(
                    {
                        "type": "warning",
                        "message": f"Line {i} exceeds 100 characters",
                        "line": i,
                        "fixable": True,
                    }
                )

        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                issues.append(
                    {
                        "type": "warning",
                        "message": f"Trailing whitespace at line {i}",
                        "line": i,
                        "fixable": True,
                    }
                )

        return issues

    def generate_suggestions(self, issues: List[Dict], file_path: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        fixable_issues = [issue for issue in issues if issue.get("fixable", False)]

        if fixable_issues:
            suggestions.append(f"Found {len(fixable_issues)} auto-fixable issues")

        if any(issue["type"] == "error" for issue in issues):
            suggestions.append("Critical errors need immediate attention")

        return suggestions

    def get_file_hash(self, file_path: str) -> str:
        """Calculate file hash for change detection"""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()


class AutoCodeFixer:
    """Automatic code fixing and optimization"""

    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer
        self.fixed_files = set()

    def fix_file(self, file_path: str) -> Dict[str, Any]:
        """Apply automatic fixes to a file"""
        backup_path = f"{file_path}.backup"

        try:
            # Create backup
            shutil.copy2(file_path, backup_path)

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            fixed_content = original_content
            file_ext = Path(file_path).suffix.lower()

            # Apply language-specific fixes
            if file_ext == ".py":
                fixed_content = self.fix_python_code(fixed_content)
            elif file_ext == ".js":
                fixed_content = self.fix_javascript_code(fixed_content)
            elif file_ext in [".html", ".css"]:
                fixed_content = self.fix_web_files(fixed_content, file_ext)

            # Apply general fixes
            fixed_content = self.apply_general_fixes(fixed_content)

            # Write fixed content if changes were made
            if fixed_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                self.fixed_files.add(file_path)
                logging.info(f"Fixed issues in {file_path}")

                return {
                    "success": True,
                    "file_path": file_path,
                    "changes_made": True,
                    "backup_created": backup_path,
                }
            else:
                # Remove backup if no changes
                os.remove(backup_path)
                return {"success": True, "file_path": file_path, "changes_made": False}

        except Exception as e:
            logging.error(f"Error fixing {file_path}: {e}")
            return {"success": False, "file_path": file_path, "error": str(e)}

    def fix_python_code(self, content: str) -> str:
        """Fix Python code issues"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Remove trailing whitespace
            fixed_line = line.rstrip()

            # Fix common Python issues
            if fixed_line.startswith("import ") and "," in fixed_line:
                # Split multiple imports
                fixed_line = self.fix_multiple_imports(fixed_line)

            fixed_lines.append(fixed_line)

        # Ensure proper newline at end of file
        result = "\n".join(fixed_lines)
        if not result.endswith("\n"):
            result += "\n"

        return result

    def fix_javascript_code(self, content: str) -> str:
        """Fix JavaScript code issues"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            fixed_line = line.rstrip()

            # Add missing semicolons
            if (
                fixed_line
                and not fixed_line.startswith("//")
                and not fixed_line.endswith(";")
                and not fixed_line.endswith("{")
                and not any(
                    x in fixed_line for x in ["if", "for", "while", "function", "=>"]
                )
            ):
                fixed_line += ";"

            fixed_lines.append(fixed_line)

        result = "\n".join(fixed_lines)
        if not result.endswith("\n"):
            result += "\n"

        return result

    def fix_web_files(self, content: str, file_ext: str) -> str:
        """Fix HTML/CSS issues"""
        if file_ext == ".html":
            # Fix self-closing tags
            content = content.replace("<br>", "<br />")
            content = content.replace("<hr>", "<hr />")
            content = content.replace("<img>", "<img />")

        return content

    def apply_general_fixes(self, content: str) -> str:
        """Apply general code fixes"""
        # Remove trailing whitespace from all lines
        lines = [line.rstrip() for line in content.split("\n")]

        # Ensure exactly one newline at end of file
        while lines and not lines[-1]:
            lines.pop()

        result = "\n".join(lines)
        if result and not result.endswith("\n"):
            result += "\n"

        return result

    def fix_multiple_imports(self, import_line: str) -> str:
        """Fix multiple imports on one line"""
        if import_line.count(",") > 0:
            parts = import_line.split("import")
            if len(parts) == 2:
                base = parts[0] + "import"
                modules = [m.strip() for m in parts[1].split(",")]
                return "\n".join([f"{base} {module}" for module in modules])
        return import_line


class FileSyncManager:
    """File synchronization and monitoring system"""

    def __init__(self, analyzer: CodeAnalyzer, fixer: AutoCodeFixer):
        self.analyzer = analyzer
        self.fixer = fixer
        self.observer = Observer()
        self.sync_interval = 5000  # ms
        self.watched_files = {}

    def start_monitoring(self, directories: List[str]):
        """Start monitoring directories for changes"""
        event_handler = CodeChangeHandler(self.analyzer, self.fixer)

        for directory in directories:
            if os.path.exists(directory):
                self.observer.schedule(event_handler, directory, recursive=True)
                logging.info(f"Started monitoring: {directory}")

        self.observer.start()
        logging.info("File synchronization monitoring started")

    def stop_monitoring(self):
        """Stop all monitoring"""
        self.observer.stop()
        self.observer.join()
        logging.info("File synchronization monitoring stopped")

    def sync_directory(self, source_dir: str, target_dir: str):
        """Synchronize directories"""
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_path, source_dir)
                    target_path = os.path.join(target_dir, relative_path)

                    # Create target directory if needed
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    # Copy file if it doesn't exist or is newer
                    if not os.path.exists(target_path) or os.path.getmtime(
                        source_path
                    ) > os.path.getmtime(target_path):
                        shutil.copy2(source_path, target_path)
                        logging.info(f"Synced: {relative_path}")

            logging.info(f"Directory sync completed: {source_dir} -> {target_dir}")

        except Exception as e:
            logging.error(f"Sync error: {e}")


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system changes for auto-fixing"""

    def __init__(self, analyzer: CodeAnalyzer, fixer: AutoCodeFixer):
        self.analyzer = analyzer
        self.fixer = fixer
        self.last_modified = {}

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return

        file_path = event.src_path
        current_time = time.time()

        # Debounce rapid modifications
        if (
            file_path in self.last_modified
            and current_time - self.last_modified[file_path] < 1.0
        ):
            return

        self.last_modified[file_path] = current_time

        # Check if file should be processed
        if self.should_process_file(file_path):
            logging.info(f"File modified: {file_path}")
            self.process_file(file_path)

    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed based on patterns"""
        config = self.analyzer.config

        # Check include patterns
        include_patterns = config.get("file_patterns", {}).get("include", [])
        exclude_patterns = config.get("file_patterns", {}).get("exclude", [])

        for pattern in exclude_patterns:
            if Path(file_path).match(pattern):
                return False

        for pattern in include_patterns:
            if Path(file_path).match(pattern):
                return True

        return False

    def process_file(self, file_path: str):
        """Analyze and fix modified file"""
        try:
            # Analyze file
            analysis = self.analyzer.analyze_file(file_path)

            # Auto-fix if enabled
            if self.analyzer.config.get("auto_fix", True) and analysis.get("issues"):

                fix_result = self.fixer.fix_file(file_path)

                if fix_result.get("changes_made"):
                    logging.info(f"Auto-fixed: {file_path}")

        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")


class BDKingR7CodeManager:
    """Main code management system"""

    def __init__(self, config_path: str = "builder.json"):
        self.analyzer = CodeAnalyzer(config_path)
        self.fixer = AutoCodeFixer(self.analyzer)
        self.sync_manager = FileSyncManager(self.analyzer, self.fixer)
        self.running = False

    def start_auto_mode(self):
        """Start automatic code fixing and synchronization"""
        self.running = True
        logging.info("Starting BD-King-R7 Auto Code Manager...")

        # Get sync directories from config
        sync_dirs = self.analyzer.config.get("sync_config", {}).get(
            "target_directories", []
        )

        # Start file monitoring
        self.sync_manager.start_monitoring(sync_dirs)

        # Initial scan and fix
        self.scan_and_fix_all()

        logging.info("Auto mode started successfully")

    def stop_auto_mode(self):
        """Stop automatic operations"""
        self.running = False
        self.sync_manager.stop_monitoring()
        logging.info("Auto mode stopped")

    def scan_and_fix_all(self):
        """Scan all files and apply fixes"""
        config = self.analyzer.config
        include_patterns = config.get("file_patterns", {}).get("include", [])

        all_files = []
        for pattern in include_patterns:
            all_files.extend(Path(".").rglob(pattern))

        fixed_count = 0
        for file_path in all_files:
            if self.should_process_file(str(file_path)):
                result = self.fixer.fix_file(str(file_path))
                if result.get("changes_made"):
                    fixed_count += 1

        logging.info(f"Scan and fix completed. Fixed {fixed_count} files.")
        return fixed_count

    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        handler = CodeChangeHandler(self.analyzer, self.fixer)
        return handler.should_process_file(file_path)

    def generate_report(self) -> Dict[str, Any]:
        """Generate system status report"""
        return {
            "status": "running" if self.running else "stopped",
            "fixed_files_count": len(self.fixer.fixed_files),
            "config": self.analyzer.config,
            "timestamp": datetime.now().isoformat(),
        }


# CLI Interface
def main():
    """Command line interface"""
    import argparse

    parser = argparse.ArgumentParser(description="BD-King-R7 Auto Code Manager")
    parser.add_argument("--config", default="builder.json", help="Config file path")
    parser.add_argument("--scan", action="store_true", help="Scan and fix all files")
    parser.add_argument("--auto", action="store_true", help="Start auto mode")
    parser.add_argument("--report", action="store_true", help="Generate report")

    args = parser.parse_args()

    manager = BDKingR7CodeManager(args.config)

    if args.scan:
        manager.scan_and_fix_all()
    elif args.auto:
        try:
            manager.start_auto_mode()
            # Keep running until interrupted
            while manager.running:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_auto_mode()
    elif args.report:
        report = manager.generate_report()
        print(json.dumps(report, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
