#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TAMANNA ULTIMATE CODE RUNNER
=====================================
আল্টিমেট কোড রানার - সমস্ত কোড এক্সিকিউট করুন
- স্বয়ংক্রিয় Python কোড রান
- JavaScript এক্সিকিউশন
- Shell স্ক্রিপ্ট এক্সিকিউশন
- ত্রুটি সনাক্তকরণ ও রিপোর্ট তৈরি
- লাইভ মনিটরিং
"""

import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path


class TamannaUltimateCodeRunner:
    def __init__(self):
        self.home = str(Path.home())
        self.repo_root = os.getcwd()
        self.reports = {
            "python": [],
            "javascript": [],
            "shell": [],
            "errors": [],
            "summary": {},
        }
        self.execution_stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now(),
            "end_time": None,
        }

    # =============================================
    # 📊 PYTHON CODE EXECUTOR
    # =============================================
    def run_python_files(self):
        """সব Python ফাইল এক্সিকিউট করুন"""
        print("\n" + "=" * 60)
        print("🐍 PYTHON CODE EXECUTION STARTED")
        print("=" * 60)

        python_files = [
            "run.py",
            "auto_code_manager.py",
            "auto_fix_issues.py",
            "lint_and_detect_issues.py",
            "ai_brain_core.py",
            "ai_system_monitor.py",
            "tamanna_master_ai.py",
            "tamanna_distributed_ai.py",
            "tamanna_head.py",
            "tamanna_security_ai.py",
            "tamanna_auto_counter.py",
            "tamanna_cli.py",
        ]

        for py_file in python_files:
            file_path = os.path.join(self.repo_root, py_file)
            if os.path.exists(file_path):
                self._execute_python(file_path, py_file)
            else:
                print(f"⏭️  SKIPPED: {py_file} (File not found)")

    def _execute_python(self, file_path, file_name):
        """Single Python file executor"""
        try:
            print(f"\n📄 Running: {file_name}")
            print(f"📍 Path: {file_path}")

            # Set timeout for execution (15 seconds max)
            result = subprocess.run(
                ["python3", file_path], capture_output=True, text=True, timeout=15
            )

            output = result.stdout
            error = result.stderr
            return_code = result.returncode

            report = {
                "file": file_name,
                "path": file_path,
                "status": "SUCCESS" if return_code == 0 else "FAILED",
                "return_code": return_code,
                "output": output[:500] if output else "No output",
                "error": error[:500] if error else "No error",
                "timestamp": datetime.now().isoformat(),
            }

            self.reports["python"].append(report)

            if return_code == 0:
                print(f"✅ SUCCESS: {file_name}")
                self.execution_stats["successful"] += 1
                if output:
                    print(f"📤 Output: {output[:200]}...")
            else:
                print(f"❌ FAILED: {file_name}")
                print(f"⚠️  Error: {error[:200]}")
                self.execution_stats["failed"] += 1
                self.reports["errors"].append(
                    {"file": file_name, "error": error, "type": "Python"}
                )

        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {file_name} (exceeded 15 seconds)")
            self.execution_stats["failed"] += 1
            self.reports["errors"].append(
                {
                    "file": file_name,
                    "error": "Execution timeout after 15 seconds",
                    "type": "Python",
                }
            )
        except Exception as e:
            print(f"💥 ERROR in {file_name}: {str(e)}")
            self.execution_stats["failed"] += 1
            self.reports["errors"].append(
                {
                    "file": file_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "type": "Python",
                }
            )

    # =============================================
    # 📊 JAVASCRIPT CODE EXECUTOR
    # =============================================
    def run_javascript_files(self):
        """সব JavaScript ফাইল এক্সিকিউট করুন"""
        print("\n" + "=" * 60)
        print("🟨 JAVASCRIPT CODE EXECUTION STARTED")
        print("=" * 60)

        js_files = [
            "index.js",
            "bot.js",
            "watcher.js",
            "auto-builder-workflow.js",
        ]

        for js_file in js_files:
            file_path = os.path.join(self.repo_root, js_file)
            if os.path.exists(file_path):
                self._execute_javascript(file_path, js_file)
            else:
                print(f"⏭️  SKIPPED: {js_file} (File not found)")

    def _execute_javascript(self, file_path, file_name):
        """Single JavaScript executor"""
        try:
            print(f"\n📄 Running: {file_name}")
            print(f"📍 Path: {file_path}")

            result = subprocess.run(
                ["node", file_path], capture_output=True, text=True, timeout=15
            )

            output = result.stdout
            error = result.stderr
            return_code = result.returncode

            report = {
                "file": file_name,
                "path": file_path,
                "status": "SUCCESS" if return_code == 0 else "FAILED",
                "return_code": return_code,
                "output": output[:500] if output else "No output",
                "error": error[:500] if error else "No error",
                "timestamp": datetime.now().isoformat(),
            }

            self.reports["javascript"].append(report)

            if return_code == 0:
                print(f"✅ SUCCESS: {file_name}")
                self.execution_stats["successful"] += 1
            else:
                print(f"❌ FAILED: {file_name}")
                print(f"⚠️  Error: {error[:200]}")
                self.execution_stats["failed"] += 1
                self.reports["errors"].append(
                    {"file": file_name, "error": error, "type": "JavaScript"}
                )

        except FileNotFoundError:
            print(f"📦 Node.js not installed. Skipping: {file_name}")
        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {file_name}")
            self.execution_stats["failed"] += 1
        except Exception as e:
            print(f"💥 ERROR in {file_name}: {str(e)}")
            self.execution_stats["failed"] += 1
            self.reports["errors"].append(
                {"file": file_name, "error": str(e), "type": "JavaScript"}
            )

    # =============================================
    # 📊 SHELL SCRIPT EXECUTOR
    # =============================================
    def run_shell_scripts(self):
        """সব Shell স্ক্রিপ্ট এক্সিকিউট করুন"""
        print("\n" + "=" * 60)
        print("🐚 SHELL SCRIPT EXECUTION STARTED")
        print("=" * 60)

        shell_files = [
            "install.sh",
            "auto_sync_all.sh",
            "tamanna_runner.sh",
            "tamanna_debug.sh",
            "check_token.sh",
        ]

        for sh_file in shell_files:
            file_path = os.path.join(self.repo_root, sh_file)
            if os.path.exists(file_path):
                self._execute_shell(file_path, sh_file)
            else:
                print(f"⏭️  SKIPPED: {sh_file} (File not found)")

    def _execute_shell(self, file_path, file_name):
        """Single Shell script executor"""
        try:
            print(f"\n📄 Running: {file_name}")
            print(f"📍 Path: {file_path}")

            # Make executable
            os.chmod(file_path, 0o755)

            result = subprocess.run(
                ["bash", file_path], capture_output=True, text=True, timeout=15
            )

            output = result.stdout
            error = result.stderr
            return_code = result.returncode

            report = {
                "file": file_name,
                "path": file_path,
                "status": "SUCCESS" if return_code == 0 else "FAILED",
                "return_code": return_code,
                "output": output[:500] if output else "No output",
                "error": error[:500] if error else "No error",
                "timestamp": datetime.now().isoformat(),
            }

            self.reports["shell"].append(report)

            if return_code == 0:
                print(f"✅ SUCCESS: {file_name}")
                self.execution_stats["successful"] += 1
            else:
                print(f"❌ FAILED: {file_name}")
                self.execution_stats["failed"] += 1

        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {file_name}")
            self.execution_stats["failed"] += 1
        except Exception as e:
            print(f"💥 ERROR in {file_name}: {str(e)}")
            self.execution_stats["failed"] += 1

    # =============================================
    # 📊 DEPENDENCY CHECK
    # =============================================
    def check_dependencies(self):
        """ডিপেন্ডেন্সি চেক করুন"""
        print("\n" + "=" * 60)
        print("📦 DEPENDENCY CHECK")
        print("=" * 60)

        deps = {
            "Python 3": "python3 --version",
            "Node.js": "node --version",
            "npm": "npm --version",
            "Bash": "bash --version",
            "Git": "git --version",
        }

        for dep_name, cmd in deps.items():
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {dep_name}: INSTALLED")
                else:
                    print(f"❌ {dep_name}: NOT FOUND")
            except:
                print(f"❌ {dep_name}: NOT FOUND")

    # =============================================
    # 📊 INSTALL DEPENDENCIES
    # =============================================
    def install_dependencies(self):
        """ডিপেন্ডেন্সি ইনস্টল করুন"""
        print("\n" + "=" * 60)
        print("📥 INSTALLING DEPENDENCIES")
        print("=" * 60)

        if os.path.exists("requirements.txt"):
            print("📦 Installing Python dependencies...")
            try:
                subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"],
                    capture_output=True,
                    timeout=60,
                )
                print("✅ Python dependencies installed")
            except Exception as e:
                print(f"❌ Failed to install Python deps: {e}")

        if os.path.exists("package.json"):
            print("📦 Installing Node.js dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    capture_output=True,
                    timeout=120,
                    cwd=self.repo_root,
                )
                print("✅ Node.js dependencies installed")
            except Exception as e:
                print(f"❌ Failed to install Node deps: {e}")

    # =============================================
    # 📊 GENERATE REPORTS
    # =============================================
    def generate_report(self):
        """সব রিপোর্ট তৈরি করুন"""
        self.execution_stats["end_time"] = datetime.now()

        # Summary Report
        summary = {
            "total_python": len(self.reports["python"]),
            "total_javascript": len(self.reports["javascript"]),
            "total_shell": len(self.reports["shell"]),
            "total_errors": len(self.reports["errors"]),
            "total_successful": self.execution_stats["successful"],
            "total_failed": self.execution_stats["failed"],
            "execution_time": str(
                self.execution_stats["end_time"] - self.execution_stats["start_time"]
            ),
            "timestamp": datetime.now().isoformat(),
        }

        self.reports["summary"] = summary

        # Save JSON Report
        report_file = "EXECUTION_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.reports, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("📊 EXECUTION REPORT")
        print("=" * 60)
        print(f"✅ Python Files Executed: {summary['total_python']}")
        print(f"✅ JavaScript Files Executed: {summary['total_javascript']}")
        print(f"✅ Shell Scripts Executed: {summary['total_shell']}")
        print(f"🟢 Successful Executions: {summary['total_successful']}")
        print(f"🔴 Failed Executions: {summary['total_failed']}")
        print(f"⚠️  Total Errors: {summary['total_errors']}")
        print(f"⏱️  Total Execution Time: {summary['execution_time']}")
        print(f"\n💾 Report saved to: {report_file}")
        print("=" * 60)

        return report_file

    # =============================================
    # 🚀 MAIN EXECUTION
    # =============================================
    def run_all(self):
        """সব কোড চালান"""
        print("\n" + "🚀" * 30)
        print("🤖 TAMANNA ULTIMATE CODE RUNNER - STARTED")
        print("🚀" * 30)

        # Step 1: Check Dependencies
        self.check_dependencies()

        # Step 2: Install Dependencies
        print("\n⏸️  Do you want to install dependencies? (y/n): ", end="")
        if input().lower() == "y":
            self.install_dependencies()

        # Step 3: Run Python Files
        self.run_python_files()

        # Step 4: Run JavaScript Files
        self.run_javascript_files()

        # Step 5: Run Shell Scripts
        self.run_shell_scripts()

        # Step 6: Generate Reports
        report_file = self.generate_report()

        # Step 7: Display Error Summary
        if self.reports["errors"]:
            print("\n" + "=" * 60)
            print("⚠️  ERROR SUMMARY")
            print("=" * 60)
            for i, err in enumerate(self.reports["errors"][:5], 1):
                print(f"\n{i}. {err['file']} ({err['type']})")
                print(f"   Error: {err['error'][:100]}...")

        print("\n" + "🎉" * 30)
        print("✅ CODE EXECUTION COMPLETED!")
        print("🎉" * 30)


if __name__ == "__main__":
    runner = TamannaUltimateCodeRunner()
    runner.run_all()
