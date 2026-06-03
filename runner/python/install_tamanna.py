#!/usr/bin/env python3
"""
Tamanna System Installer - Multi-Platform
"""

import os
import platform
from pathlib import Path


class TamannaInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.install_dir = Path.home() / "tamanna_system"

    def install(self):
        print("Installing Tamanna Code Language System...")

        # Create installation directory
        self.install_dir.mkdir(exist_ok=True)

        # Copy system files
        self.copy_files()

        # Platform-specific setup
        if self.system == "windows":
            self.setup_windows()
        elif self.system == "linux":
            self.setup_linux()
        elif "android" in platform.platform().lower():
            self.setup_android()

        # Create startup scripts
        self.create_startup_scripts()

        print("Installation completed successfully!")
        print(f"Tamanna system installed in: {self.install_dir}")

    def copy_files(self):
        """Copy system files to installation directory"""
        files_to_copy = ["tamanna_system.py",
                         "tamanna_config.hm", "requirements.txt"]

        for file in files_to_copy:
            if Path(file).exists():
                shutil.copy2(file, self.install_dir / file)
                print(f"Copied: {file}")

    def setup_windows(self):
        """Windows-specific setup"""
        # Create batch file
        batch_content = """@echo off
echo Tamanna Code Language System
python %~dp0tamanna_system.py %*
"""
        batch_file = self.install_dir / "tamanna.bat"
        with open(batch_file, "w") as f:
            f.write(batch_content)

        print("Created Windows batch file")

    def setup_linux(self):
        """Linux-specific setup"""
        # Create shell script
        script_content = """#!/bin/bash
echo "Tamanna Code Language System"
python3 "$(dirname "$0")/tamanna_system.py" "$@"
"""
        script_file = self.install_dir / "tamanna"
        with open(script_file, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_file, 0o755)
        print("Created Linux shell script")

    def setup_android(self):
        """Android-specific setup"""
        script_content = """#!/bin/bash
echo "Tamanna on Android"
python "$(dirname "$0")/tamanna_system.py" "$@"
"""
        script_file = self.install_dir / "tamanna_android"
        with open(script_file, "w") as f:
            f.write(script_content)

        os.chmod(script_file, 0o755)
        print("Created Android shell script")

    def create_startup_scripts(self):
        """Create platform-specific startup scripts"""
        # Add to PATH (conceptual - would need admin rights)
        print("Please add the following to your PATH:")
        print(f"  {self.install_dir}")


if __name__ == "__main__":
    installer = TamannaInstaller()
    installer.install()
