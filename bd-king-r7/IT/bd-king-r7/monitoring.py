#!/usr/bin/env python3
"""
BD-King-R7 Advanced Code Monitoring System
"""

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class CodeMetric:
    """Code quality metrics data class"""

    cyclomatic_complexity: float
    maintainability_index: float
    code_duplication_percent: float
    comment_density_percent: float
    technical_debt_ratio: float


@dataclass
class SecurityMetric:
    """Security metrics data class"""

    vulnerabilities_count: int
    secrets_detected: int
    dependency_issues: int
    security_score: float


@dataclass
class MonitoringEvent:
    """Monitoring event data class"""

    timestamp: str
    project: Dict[str, str]
    metrics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    changes: Dict[str, Any]


class CodeMonitor:
    """Advanced code monitoring system"""

    def __init__(self, config_path: str = "code.monitoring.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.observer = Observer()
        self.monitoring_data = []
        self.alert_history = []
        self.running = False

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file {config_path} not found")
            raise

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_config = self.config.get("logging", {})
        logging.basicConfig(
            level=getattr(logging, log_config.get("level", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_config.get(
                    "file", "code_monitor.log")),
                logging.StreamHandler(),
            ],
        )

    def start_monitoring(self):
        """Start the monitoring system"""
        if self.running:
            logging.warning("Monitoring already running")
            return

        self.running = True
        logging.info("Starting BD-King-R7 Code Monitoring System")

        # Start file system monitoring
        if self.config["real_time_monitoring"]["enabled"]:
            self.start_file_monitoring()

        # Start performance monitoring
        if self.config["tracked_metrics"]["performance"]["enabled"]:
            self.start_performance_monitoring()

        # Start periodic scans
        self.start_periodic_scans()

        logging.info("Code monitoring system started successfully")

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()
        logging.info("Code monitoring system stopped")

    def start_file_monitoring(self):
        """Start monitoring file system changes"""
        event_handler = CodeChangeHandler(self)

        # Monitor current directory and subdirectories
        self.observer.schedule(event_handler, ".", recursive=True)
        self.observer.start()
        logging.info("File system monitoring started")

    def start_performance_monitoring(self):
        """Start performance monitoring thread"""

        def performance_monitor():
            while self.running:
                try:
                    performance_data = self.collect_performance_metrics()
                    self.analyze_performance(performance_data)
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logging.error(f"Performance monitoring error: {e}")

        thread = threading.Thread(target=performance_monitor, daemon=True)
        thread.start()
        logging.info("Performance monitoring started")

    def start_periodic_scans(self):
        """Start periodic code quality scans"""

        def periodic_scanner():
            while self.running:
                try:
                    self.run_full_scan()
                    # Run scan based on configured interval
                    interval = self.config["real_time_monitoring"].get(
                        "polling_interval_seconds", 300
                    )
                    time.sleep(interval)
                except Exception as e:
                    logging.error(f"Periodic scan error: {e}")

        thread = threading.Thread(target=periodic_scanner, daemon=True)
        thread.start()
        logging.info("Periodic scans started")

    def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage(".").percent,
            "active_processes": len(psutil.pids()),
        }

    def analyze_performance(self, metrics: Dict[str, Any]):
        """Analyze performance metrics and trigger alerts"""
        thresholds = self.config["tracked_metrics"]["performance"]["thresholds"]

        if metrics["cpu_percent"] > thresholds["max_cpu_percent"]:
            self.trigger_alert(
                "high_cpu_usage",
                f"High CPU usage detected: {metrics['cpu_percent']}%",
                "high",
            )

        if metrics["memory_usage"] > 80:  # Default threshold
            self.trigger_alert(
                "high_memory_usage",
                f"High memory usage: {metrics['memory_usage']}%",
                "high",
            )

    def run_full_scan(self):
        """Run comprehensive code scan"""
        logging.info("Starting full code scan")

        try:
            # Collect code metrics
            code_metrics = self.analyze_code_quality()
            security_metrics = self.analyze_security()
            coverage_metrics = self.analyze_test_coverage()

            # Create monitoring event
            event = MonitoringEvent(
                timestamp=datetime.now().isoformat(),
                project={
                    "name": self.config["monitoring_system"]["name"],
                    "version": self.config["monitoring_system"]["version"],
                    "branch": self.get_current_branch(),
                    "commit_hash": self.get_current_commit(),
                },
                metrics={
                    "code_quality": asdict(code_metrics),
                    "security": asdict(security_metrics),
                    "coverage": coverage_metrics,
                },
                issues=self.detect_issues(),
                changes=self.get_recent_changes(),
            )

            # Store event
            self.monitoring_data.append(asdict(event))

            # Check thresholds and trigger alerts
            self.check_quality_gates(asdict(event))

            # Save monitoring data
            self.save_monitoring_data()

            logging.info("Full code scan completed")

        except Exception as e:
            logging.error(f"Full scan failed: {e}")

    def analyze_code_quality(self) -> CodeMetric:
        """Analyze code quality metrics"""
        # This would integrate with tools like pylint, radon, etc.
        # For now, return mock data
        return CodeMetric(
            cyclomatic_complexity=8.5,
            maintainability_index=72.3,
            code_duplication_percent=3.2,
            comment_density_percent=15.8,
            technical_debt_ratio=0.8,
        )

    def analyze_security(self) -> SecurityMetric:
        """Analyze security metrics"""
        # This would integrate with security scanning tools
        return SecurityMetric(
            vulnerabilities_count=2,
            secrets_detected=0,
            dependency_issues=1,
            security_score=85.5,
        )

    def analyze_test_coverage(self) -> Dict[str, float]:
        """Analyze test coverage"""
        # This would integrate with coverage tools
        return {
            "line_coverage_percent": 78.5,
            "branch_coverage_percent": 65.2,
            "function_coverage_percent": 82.1,
        }

    def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect code issues based on custom rules"""
        issues = []
        custom_rules = self.config.get(
            "custom_rules", {}).get("business_rules", [])

        for rule in custom_rules:
            # Implement rule checking logic here
            # This would scan files for patterns and create issues
            pass

        return issues

    def get_recent_changes(self) -> Dict[str, Any]:
        """Get recent code changes"""
        # This would integrate with git to get recent changes
        return {
            "files_modified": 5,
            "lines_added": 120,
            "lines_deleted": 45,
            "files_added": ["new_feature.py"],
            "files_deleted": [],
        }

    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def get_current_commit(self) -> str:
        """Get current git commit hash"""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"

    def trigger_alert(self, alert_type: str, message: str, severity: str):
        """Trigger an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "acknowledged": False,
        }

        self.alert_history.append(alert)
        logging.warning(f"ALERT [{severity.upper()}]: {message}")

        # Send notifications based on configuration
        self.send_notifications(alert)

    def send_notifications(self, alert: Dict[str, Any]):
        """Send alert notifications"""
        alert_config = self.config["alert_system"]

        if not alert_config["enabled"]:
            return

        channels = alert_config.get("channels", [])

        if "console" in channels:
            print(f"🚨 {alert['severity'].upper()} ALERT: {alert['message']}")

        if "log_file" in channels:
            logging.warning(f"ALERT: {alert}")

        if (
            "webhook" in channels
            and alert_config["notifications"]["webhook"]["enabled"]
        ):
            self.send_webhook_alert(alert)

    def send_webhook_alert(self, alert: Dict[str, Any]):
        """Send alert to webhook"""
        # Implement webhook notification
        pass

    def check_quality_gates(self, event_data: Dict[str, Any]):
        """Check quality gates and trigger alerts if failed"""
        quality_gates = self.config["custom_rules"]["quality_gates"]
        metrics = event_data["metrics"]

        # Check pre-commit quality gates
        if (
            metrics["coverage"]["line_coverage_percent"]
            < quality_gates["pre_commit"]["min_test_coverage"]
        ):
            self.trigger_alert(
                "low_test_coverage",
                f"Test coverage {metrics['coverage']['line_coverage_percent']}% below minimum {quality_gates['pre_commit']['min_test_coverage']}%",
                "medium",
            )

        if (
            metrics["code_quality"]["cyclomatic_complexity"]
            > quality_gates["pre_commit"]["max_complexity"]
        ):
            self.trigger_alert(
                "high_complexity",
                f"Code complexity {metrics['code_quality']['cyclomatic_complexity']} above maximum {quality_gates['pre_commit']['max_complexity']}",
                "medium",
            )

    def save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            data_file = "monitoring_data.json"
            with open(data_file, "w") as f:
                json.dump(
                    {
                        "last_updated": datetime.now().isoformat(),
                        # Keep last 100 events
                        "events": self.monitoring_data[-100:],
                        # Keep last 50 alerts
                        "alerts": self.alert_history[-50:],
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logging.error(f"Failed to save monitoring data: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate monitoring report"""
        if not self.monitoring_data:
            return {"error": "No monitoring data available"}

        latest_event = self.monitoring_data[-1]

        return {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_scans": len(self.monitoring_data),
                "total_alerts": len(self.alert_history),
                "current_quality_score": latest_event["metrics"]["code_quality"][
                    "maintainability_index"
                ],
                "current_security_score": latest_event["metrics"]["security"][
                    "security_score"
                ],
            },
            "current_metrics": latest_event["metrics"],
            "recent_alerts": self.alert_history[-10:],
            "quality_trends": self.calculate_trends(),
        }

    def calculate_trends(self) -> Dict[str, Any]:
        """Calculate quality trends over time"""
        if len(self.monitoring_data) < 2:
            return {"trend": "insufficient_data"}

        recent_data = self.monitoring_data[-5:]  # Last 5 scans

        trends = {}
        for metric in [
            "maintainability_index",
            "security_score",
            "line_coverage_percent",
        ]:
            values = [
                event["metrics"]["code_quality"].get(metric, 0) for event in recent_data
            ]
            if len(values) > 1:
                trend = (
                    "improving"
                    if values[-1] > values[0]
                    else "declining" if values[-1] < values[0] else "stable"
                )
                trends[metric] = {
                    "trend": trend,
                    "change": round(values[-1] - values[0], 2),
                }

        return trends


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system changes for code monitoring"""

    def __init__(self, monitor: CodeMonitor):
        self.monitor = monitor
        self.last_events = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if self.should_monitor_file(file_path):
            logging.info(f"File modified: {file_path}")
            self.monitor.trigger_alert(
                "file_modified", f"File {file_path} was modified", "low"
            )

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if self.should_monitor_file(file_path):
            logging.info(f"File created: {file_path}")
            self.monitor.trigger_alert(
                "file_created", f"New file {file_path} was created", "low"
            )

    def on_deleted(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if self.should_monitor_file(file_path):
            logging.info(f"File deleted: {file_path}")
            self.monitor.trigger_alert(
                "file_deleted", f"File {file_path} was deleted", "medium"
            )

    def should_monitor_file(self, file_path: str) -> bool:
        """Check if file should be monitored based on patterns"""
        config = self.monitor.config["file_monitoring"]

        # Check excluded patterns
        for pattern in config["excluded_patterns"]:
            if Path(file_path).match(pattern):
                return False

        # Check included patterns
        for pattern in config["included_patterns"]:
            if Path(file_path).match(pattern):
                return True

        return False


# CLI Interface
def main():
    """Command line interface for code monitoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description="BD-King-R7 Code Monitoring System")
    parser.add_argument(
        "--config", default="code.monitoring.json", help="Monitoring config file"
    )
    parser.add_argument("--start", action="store_true",
                        help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--scan", action="store_true",
                        help="Run one-time scan")
    parser.add_argument("--report", action="store_true",
                        help="Generate report")

    args = parser.parse_args()

    monitor = CodeMonitor(args.config)

    try:
        if args.scan:
            monitor.run_full_scan()
            print("Scan completed")
        elif args.report:
            report = monitor.generate_report()
            print(json.dumps(report, indent=2))
        elif args.start:
            monitor.start_monitoring()
            try:
                while monitor.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        elif args.stop:
            monitor.stop_monitoring()
        else:
            parser.print_help()

    except Exception as e:
        logging.error(f"Monitoring error: {e}")


if __name__ == "__main__":
    main()
