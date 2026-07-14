#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tamanna System Configuration - Advanced Edition
Features: JSON/YAML config, env overrides, logging, platform detection, dynamic ports
"""

import os
import sys
import json
import logging
import socket
import platform as plat
from pathlib import Path
from typing import Dict, Any, Optional

# ---------- Advanced logging setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("TamannaSystem")


# ---------- Configuration class ----------
class TamannaConfig:
    """Central configuration manager with overrides and validation"""

    DEFAULTS = {
        "system_name": "Tamanna Code Language",
        "version": "1.0.0",
        "platform": "multi",
        "color_scheme": "7-colors",
        "syntax_highlighting": True,
        "auto_build": True,
        "build_directory": "./build",
        "dist_directory": "./dist",
        "default_port": 8080,
        "enable_network": True,
        "shell": None,  # Will be auto-detected
        "log_level": "INFO",
        "config_file": "tamanna_config.json",
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULTS.copy()
        self.config_path = config_path or self.DEFAULTS["config_file"]
        self._load_config_file()
        self._apply_env_overrides()
        self._detect_platform_shell()
        self._validate_port()
        self._setup_logging_level()
        logger.info(
            f"Configuration loaded: {self.get('system_name')} v{self.get('version')}"
        )

    def _load_config_file(self):
        """Load JSON or YAML config file if exists"""
        path = Path(self.config_path)
        if not path.exists():
            logger.debug(f"No config file found at {path}, using defaults")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix in [".yaml", ".yml"]:
                    try:
                        import yaml

                        data = yaml.safe_load(f)
                    except ImportError:
                        logger.warning("PyYAML not installed, falling back to JSON")
                        f.seek(0)
                        data = json.load(f)
                else:
                    data = json.load(f)
            self.config.update(data)
            logger.info(f"Loaded config from {path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def _apply_env_overrides(self):
        """Override settings with environment variables (TAMANNA_*)"""
        for key in self.config.keys():
            env_var = f"TAMANNA_{key.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var]
                # Type conversion
                if isinstance(self.config[key], bool):
                    value = value.lower() in ("true", "1", "yes")
                elif isinstance(self.config[key], int):
                    value = int(value)
                self.config[key] = value
                logger.debug(f"Override {key} = {value} from env {env_var}")

    def _detect_platform_shell(self):
        """Cross-platform shell detection (advanced)"""
        system = plat.system().lower()
        platform_map = {
            "windows": ("cmd", "powershell"),
            "linux": ("bash", "zsh", "dash"),
            "darwin": ("zsh", "bash"),  # macOS
            "android": ("termux", "bash"),
            "ios": ("zsh", "bash"),
        }
        # Detect exact platform
        if system == "windows":
            detected_platform = "windows"
            shell = os.environ.get("COMSPEC", "cmd.exe")
        elif system == "linux":
            # Check for Termux (Android)
            if "com.termux" in os.environ.get("PREFIX", ""):
                detected_platform = "android"
                shell = "termux"
            else:
                detected_platform = "linux"
                shell = os.environ.get("SHELL", "/bin/bash").split("/")[-1]
        elif system == "darwin":
            detected_platform = "macos"
            shell = os.environ.get("SHELL", "/bin/zsh").split("/")[-1]
        else:
            detected_platform = "unknown"
            shell = "unknown"

        self.config["platform"] = detected_platform
        if not self.config["shell"]:  # only if not manually set
            self.config["shell"] = shell

    def _validate_port(self):
        """Ensure port is available and in valid range"""
        port = self.config["default_port"]
        if not (1024 <= port <= 65535):
            logger.warning(f"Port {port} out of range, resetting to 8080")
            self.config["default_port"] = 8080
            port = 8080

        if self.config["enable_network"]:
            if not self.is_port_available(port):
                new_port = self.find_free_port(port)
                logger.warning(f"Port {port} is busy, using {new_port} instead")
                self.config["default_port"] = new_port

    def _setup_logging_level(self):
        """Set logging level from config"""
        level_name = self.config.get("log_level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        logger.setLevel(level)

    # ---------- Public methods ----------
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        logger.debug(f"Set {key} = {value}")

    def save_config(self, path: Optional[str] = None):
        """Save current config to JSON file"""
        save_path = path or self.config_path
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Config saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    @staticmethod
    def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
        """Check if a port is free"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return True
            except OSError:
                return False

    @staticmethod
    def find_free_port(start_port: int, max_attempts: int = 10) -> int:
        """Find next available port"""
        for offset in range(max_attempts):
            port = start_port + offset
            if TamannaConfig.is_port_available(port):
                return port
        return start_port + max_attempts  # fallback

    def display_summary(self):
        """Pretty print configuration"""
        print("\n" + "=" * 50)
        print(f"🟢 Tamanna System Configuration (v{self.get('version')})")
        print("=" * 50)
        for key, value in self.config.items():
            print(f"  {key:20} : {value}")
        print("=" * 50 + "\n")


# ---------- Plugin / Auto-discovery (advanced) ----------
def discover_plugins(plugin_dir: str = "./plugins"):
    """Auto-discover and load modules from plugins directory"""
    plugin_path = Path(plugin_dir)
    if not plugin_path.exists():
        plugin_path.mkdir(exist_ok=True)
        logger.info(f"Created plugins directory at {plugin_path}")
        return []

    plugins = []
    for file in plugin_path.glob("*.py"):
        if file.name.startswith("_"):
            continue
        plugin_name = file.stem
        try:
            # Dynamic import
            import importlib.util

            spec = importlib.util.spec_from_file_location(plugin_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugins.append(plugin_name)
            logger.info(f"Loaded plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
    return plugins


# ---------- Main execution ----------
def main():
    """Run the upgraded configuration system"""
    # 1. Initialize config
    config = TamannaConfig()  # looks for tamanna_config.json or env vars

    # 2. Override some settings programmatically (example)
    if config.get("auto_build"):
        build_dir = Path(config.get("build_directory"))
        build_dir.mkdir(exist_ok=True)
        logger.info(f"Build directory ready: {build_dir.resolve()}")

    # 3. Discover plugins (advanced)
    plugins = discover_plugins()
    if plugins:
        logger.info(f"Active plugins: {', '.join(plugins)}")

    # 4. Network check if enabled
    if config.get("enable_network"):
        port = config.get("default_port")
        logger.info(f"Network enabled – will use port {port}")

    # 5. Display final configuration
    config.display_summary()

    # 6. Optional: interactive shell (advanced)
    if "--interactive" in sys.argv or "-i" in sys.argv:
        print("Entering interactive Tamanna shell. Type 'exit' to quit.")
        while True:
            cmd = input("tamanna> ").strip()
            if cmd.lower() in ("exit", "quit"):
                break
            elif cmd.startswith("set "):
                parts = cmd[4:].split("=", 1)
                if len(parts) == 2:
                    config.set(parts[0].strip(), parts[1].strip())
                else:
                    print("Usage: set key=value")
            elif cmd == "show":
                config.display_summary()
            elif cmd == "save":
                config.save_config()
            else:
                print(f"Unknown command: {cmd}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
