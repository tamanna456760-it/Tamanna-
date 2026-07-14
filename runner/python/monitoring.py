"""
TI-PULS Monitoring Module - Advanced Real-Time System Monitoring & Observability
Comprehensive monitoring, alerting, and performance tracking for BD-King-R7
"""

import asyncio
import json
import logging
import statistics
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import GPUtil
import psutil
from prometheus_client import Gauge, start_http_server


class MonitorType(Enum):
    """Monitoring types"""

    SYSTEM = "system"
    APPLICATION = "application"
    NETWORK = "network"
    SECURITY = "security"
    BUSINESS = "business"
    PERFORMANCE = "performance"


class AlertLevel(Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealthStatus(Enum):
    """System health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class MetricData:
    """Metric data point"""

    metric_id: str
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Monitoring alert"""

    alert_id: str
    title: str
    description: str
    level: AlertLevel
    source: str
    metric: str
    current_value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class SystemHealth:
    """System health status"""

    overall_status: HealthStatus
    component_status: Dict[str, HealthStatus]
    metrics: Dict[str, float]
    last_updated: datetime
    recommendations: List[str]


@dataclass
class PerformanceReport:
    """Performance analysis report"""

    report_id: str
    period_start: datetime
    period_end: datetime
    metrics_analyzed: int
    performance_score: float
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    trends: Dict[str, Any]


class AdvancedMonitoringSystem:
    """
    Advanced Monitoring System for TI-PULS with real-time observability
    and intelligent alerting capabilities
    """

    def __init__(self, config_path: str = "config/monitoring_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_monitoring_logging()

        # Core monitoring components
        self.metrics_store = defaultdict(lambda: deque(maxlen=10000))
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=5000)
        self.health_checkers: Dict[str, Callable] = {}

        # Real-time monitoring
        self.monitoring_threads = {}
        self.is_monitoring = False
        self.collection_interval = self.config["collection_interval"]

        # Alerting system
        self.alert_rules = {}
        self.notification_handlers = {}

        # Performance analysis
        self.performance_analyzer = PerformanceAnalyzer()
        self.anomaly_detector = AnomalyDetectionEngine()

        # Visualization and reporting
        self.dashboard_manager = DashboardManager()
        self.report_generator = ReportGenerator()

        # External integrations
        self.prometheus_exporter = PrometheusExporter()
        self.external_monitors = {}

        # System baseline
        self.system_baseline = {}
        self.performance_baseline = {}

        self.logger.info("📊 Advanced Monitoring System Initialized")
        self.logger.info("🔍 Real-time Monitoring: Active")
        self.logger.info("🚨 Intelligent Alerting: Enabled")
        self.logger.info("📈 Performance Analytics: Ready")

    def _setup_monitoring_logging(self):
        """Setup monitoring-specific logging"""
        logger = logging.getLogger("MonitoringSystem")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "📊 %(asctime)s | MONITORING | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler
        file_handler = logging.FileHandler("logs/monitoring.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "collection_interval": 5,
            "metrics_retention_days": 30,
            "alert_rules": {
                "cpu_threshold": 85.0,
                "memory_threshold": 90.0,
                "disk_threshold": 95.0,
                "response_time_threshold": 2.0,
                "error_rate_threshold": 1.0,
            },
            "health_checks": {
                "system_health_interval": 60,
                "application_health_interval": 30,
                "network_health_interval": 120,
            },
            "notifications": {
                "enabled": True,
                "channels": ["email", "slack", "webhook"],
                "critical_alerts_immediate": True,
            },
            "performance_analysis": {
                "enabled": True,
                "analysis_interval": 300,
                "trend_detection": True,
            },
        }

        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            self._save_config(default_config, config_path)

        return default_config

    async def start_monitoring(self):
        """Start comprehensive monitoring system"""
        self.logger.info("🚀 Starting Advanced Monitoring System...")
        self.is_monitoring = True

        # Start all monitoring subsystems
        tasks = [
            self._start_system_monitoring(),
            self._start_application_monitoring(),
            self._start_network_monitoring(),
            self._start_security_monitoring(),
            self._start_performance_analysis(),
            self._start_alert_processor(),
            self._start_health_checker(),
            self._start_prometheus_exporter(),
        ]

        await asyncio.gather(*tasks)

        self.logger.info("✅ Monitoring System Running at Full Capacity")

    async def _start_system_monitoring(self):
        """Start system resource monitoring"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()

                # Store metrics
                for metric in system_metrics:
                    await self._store_metric(metric)

                # Check alerts
                await self._check_system_alerts(system_metrics)

                # Update system health
                await self._update_system_health(system_metrics)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"💻 System monitoring error: {e}")
                await asyncio.sleep(self.collection_interval * 2)

    async def _start_application_monitoring(self):
        """Start application performance monitoring"""
        while self.is_monitoring:
            try:
                # Collect application metrics
                app_metrics = await self._collect_application_metrics()

                # Store metrics
                for metric in app_metrics:
                    await self._store_metric(metric)

                # Check application alerts
                await self._check_application_alerts(app_metrics)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"📱 Application monitoring error: {e}")
                await asyncio.sleep(self.collection_interval * 2)

    async def _start_network_monitoring(self):
        """Start network monitoring"""
        while self.is_monitoring:
            try:
                # Collect network metrics
                network_metrics = await self._collect_network_metrics()

                # Store metrics
                for metric in network_metrics:
                    await self._store_metric(metric)

                # Check network alerts
                await self._check_network_alerts(network_metrics)

                # Less frequent
                await asyncio.sleep(self.collection_interval * 2)

            except Exception as e:
                self.logger.error(f"🌐 Network monitoring error: {e}")
                await asyncio.sleep(self.collection_interval * 4)

    async def _start_security_monitoring(self):
        """Start security monitoring"""
        while self.is_monitoring:
            try:
                # Collect security metrics
                security_metrics = await self._collect_security_metrics()

                # Store metrics
                for metric in security_metrics:
                    await self._store_metric(metric)

                # Check security alerts
                await self._check_security_alerts(security_metrics)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"🔒 Security monitoring error: {e}")
                await asyncio.sleep(self.collection_interval * 2)

    async def _start_performance_analysis(self):
        """Start performance analysis engine"""
        while self.is_monitoring:
            try:
                # Analyze performance trends
                await self._analyze_performance_trends()

                # Detect anomalies
                await self._detect_performance_anomalies()

                # Generate performance insights
                await self._generate_performance_insights()

                await asyncio.sleep(
                    self.config["performance_analysis"]["analysis_interval"]
                )

            except Exception as e:
                self.logger.error(f"📈 Performance analysis error: {e}")
                await asyncio.sleep(300)  # 5 minutes

    async def _start_alert_processor(self):
        """Start alert processing system"""
        while self.is_monitoring:
            try:
                # Process active alerts
                await self._process_active_alerts()

                # Clean up old alerts
                await self._cleanup_old_alerts()

                # Send notifications for critical alerts
                await self._send_alert_notifications()

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"🚨 Alert processor error: {e}")
                await asyncio.sleep(30)

    async def _start_health_checker(self):
        """Start system health checking"""
        while self.is_monitoring:
            try:
                # Perform health checks
                health_status = await self._perform_health_checks()

                # Update health status
                await self._update_health_status(health_status)

                # Generate health reports
                if health_status.overall_status != HealthStatus.HEALTHY:
                    await self._generate_health_report(health_status)

                await asyncio.sleep(
                    self.config["health_checks"]["system_health_interval"]
                )

            except Exception as e:
                self.logger.error(f"❤️ Health checker error: {e}")
                await asyncio.sleep(60)

    async def _start_prometheus_exporter(self):
        """Start Prometheus metrics exporter"""
        try:
            # Start Prometheus HTTP server
            start_http_server(8000)
            self.logger.info("📊 Prometheus exporter started on port 8000")
        except Exception as e:
            self.logger.error(f"❌ Prometheus exporter failed: {e}")

    async def _collect_system_metrics(self) -> List[MetricData]:
        """Collect comprehensive system metrics"""
        metrics = []
        current_time = datetime.now()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metrics = [
                MetricData(
                    "cpu_usage",
                    "CPU Usage",
                    cpu_percent,
                    "percent",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "cpu_cores",
                    "CPU Cores",
                    psutil.cpu_count(),
                    "count",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "cpu_frequency",
                    "CPU Frequency",
                    psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    "MHz",
                    current_time,
                    {"type": "system"},
                ),
            ]
            metrics.extend(cpu_metrics)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_metrics = [
                MetricData(
                    "memory_usage",
                    "Memory Usage",
                    memory.percent,
                    "percent",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "memory_used",
                    "Memory Used",
                    memory.used / (1024**3),
                    "GB",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "memory_available",
                    "Memory Available",
                    memory.available / (1024**3),
                    "GB",
                    current_time,
                    {"type": "system"},
                ),
            ]
            metrics.extend(memory_metrics)

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_metrics = [
                MetricData(
                    "disk_usage",
                    "Disk Usage",
                    disk.percent,
                    "percent",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "disk_used",
                    "Disk Used",
                    disk.used / (1024**3),
                    "GB",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "disk_free",
                    "Disk Free",
                    disk.free / (1024**3),
                    "GB",
                    current_time,
                    {"type": "system"},
                ),
            ]
            metrics.extend(disk_metrics)

            # GPU metrics (if available)
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_metrics = [
                        MetricData(
                            f"gpu_{i}_usage",
                            f"GPU {i} Usage",
                            gpu.load * 100,
                            "percent",
                            current_time,
                            {"type": "gpu"},
                        ),
                        MetricData(
                            f"gpu_{i}_memory",
                            f"GPU {i} Memory",
                            gpu.memoryUtil * 100,
                            "percent",
                            current_time,
                            {"type": "gpu"},
                        ),
                        MetricData(
                            f"gpu_{i}_temperature",
                            f"GPU {i} Temperature",
                            gpu.temperature,
                            "celsius",
                            current_time,
                            {"type": "gpu"},
                        ),
                    ]
                    metrics.extend(gpu_metrics)
            except Exception as e:
                self.logger.debug(f"GPU monitoring not available: {e}")

            # System info
            system_metrics = [
                MetricData(
                    "system_uptime",
                    "System Uptime",
                    time.time() - psutil.boot_time(),
                    "seconds",
                    current_time,
                    {"type": "system"},
                ),
                MetricData(
                    "process_count",
                    "Process Count",
                    len(psutil.pids()),
                    "count",
                    current_time,
                    {"type": "system"},
                ),
            ]
            metrics.extend(system_metrics)

        except Exception as e:
            self.logger.error(f"❌ System metrics collection error: {e}")

        return metrics

    async def _collect_application_metrics(self) -> List[MetricData]:
        """Collect application-specific metrics"""
        metrics = []
        current_time = datetime.now()

        try:
            # TI-PULS specific metrics
            app_metrics = [
                MetricData(
                    "ai_models_loaded",
                    "AI Models Loaded",
                    len(getattr(self, "ai_models", {})),
                    "count",
                    current_time,
                    {"type": "application"},
                ),
                MetricData(
                    "active_workflows",
                    "Active Workflows",
                    len(getattr(self, "active_workflows", {})),
                    "count",
                    current_time,
                    {"type": "application"},
                ),
                MetricData(
                    "decision_queue_size",
                    "Decision Queue Size",
                    getattr(self, "decision_queue_size", 0),
                    "count",
                    current_time,
                    {"type": "application"},
                ),
                MetricData(
                    "api_response_time",
                    "API Response Time",
                    self._measure_api_response_time(),
                    "milliseconds",
                    current_time,
                    {"type": "application"},
                ),
                MetricData(
                    "data_processing_rate",
                    "Data Processing Rate",
                    self._calculate_processing_rate(),
                    "records/second",
                    current_time,
                    {"type": "application"},
                ),
            ]
            metrics.extend(app_metrics)

        except Exception as e:
            self.logger.error(f"❌ Application metrics collection error: {e}")

        return metrics

    async def _collect_network_metrics(self) -> List[MetricData]:
        """Collect network metrics"""
        metrics = []
        current_time = datetime.now()

        try:
            # Network I/O
            net_io = psutil.net_io_counters()
            network_metrics = [
                MetricData(
                    "network_bytes_sent",
                    "Network Bytes Sent",
                    net_io.bytes_sent,
                    "bytes",
                    current_time,
                    {"type": "network"},
                ),
                MetricData(
                    "network_bytes_recv",
                    "Network Bytes Received",
                    net_io.bytes_recv,
                    "bytes",
                    current_time,
                    {"type": "network"},
                ),
                MetricData(
                    "network_packets_sent",
                    "Network Packets Sent",
                    net_io.packets_sent,
                    "count",
                    current_time,
                    {"type": "network"},
                ),
                MetricData(
                    "network_packets_recv",
                    "Network Packets Received",
                    net_io.packets_recv,
                    "count",
                    current_time,
                    {"type": "network"},
                ),
            ]
            metrics.extend(network_metrics)

            # Network connections
            connections = psutil.net_connections()
            connection_metrics = [
                MetricData(
                    "network_connections",
                    "Network Connections",
                    len(connections),
                    "count",
                    current_time,
                    {"type": "network"},
                ),
                MetricData(
                    "established_connections",
                    "Established Connections",
                    len([c for c in connections if c.status == "ESTABLISHED"]),
                    "count",
                    current_time,
                    {"type": "network"},
                ),
            ]
            metrics.extend(connection_metrics)

        except Exception as e:
            self.logger.error(f"❌ Network metrics collection error: {e}")

        return metrics

    async def _collect_security_metrics(self) -> List[MetricData]:
        """Collect security-related metrics"""
        metrics = []
        current_time = datetime.now()

        try:
            # Security events
            security_metrics = [
                MetricData(
                    "failed_login_attempts",
                    "Failed Login Attempts",
                    self._count_failed_logins(),
                    "count",
                    current_time,
                    {"type": "security"},
                ),
                MetricData(
                    "security_events",
                    "Security Events",
                    len(getattr(self, "security_events", [])),
                    "count",
                    current_time,
                    {"type": "security"},
                ),
                MetricData(
                    "intrusion_attempts",
                    "Intrusion Attempts",
                    self._count_intrusion_attempts(),
                    "count",
                    current_time,
                    {"type": "security"},
                ),
                MetricData(
                    "firewall_blocks",
                    "Firewall Blocks",
                    self._count_firewall_blocks(),
                    "count",
                    current_time,
                    {"type": "security"},
                ),
            ]
            metrics.extend(security_metrics)

        except Exception as e:
            self.logger.error(f"❌ Security metrics collection error: {e}")

        return metrics

    async def _store_metric(self, metric: MetricData):
        """Store metric in the metrics store"""
        self.metrics_store[metric.metric_id].append(metric)

        # Update Prometheus metrics
        await self.prometheus_exporter.update_metric(metric)

    async def _check_system_alerts(self, metrics: List[MetricData]):
        """Check system metrics against alert rules"""
        for metric in metrics:
            if metric.metric_id in self.config["alert_rules"]:
                threshold = self.config["alert_rules"][metric.metric_id]

                if metric.value > threshold:
                    await self._create_alert(
                        title=f"High {metric.name}",
                        description=f"{metric.name} is at {metric.value}{metric.unit}, exceeding threshold of {threshold}{metric.unit}",
                        level=(
                            AlertLevel.HIGH
                            if metric.value > threshold * 1.2
                            else AlertLevel.MEDIUM
                        ),
                        source="system_monitoring",
                        metric=metric.metric_id,
                        current_value=metric.value,
                        threshold=threshold,
                    )

    async def _check_application_alerts(self, metrics: List[MetricData]):
        """Check application metrics against alert rules"""
        for metric in metrics:
            # Application-specific alert rules
            if (
                metric.metric_id == "api_response_time" and metric.value > 2000
            ):  # 2 seconds
                await self._create_alert(
                    title="High API Response Time",
                    description=f"API response time is {metric.value}ms, exceeding acceptable limits",
                    level=AlertLevel.MEDIUM,
                    source="application_monitoring",
                    metric=metric.metric_id,
                    current_value=metric.value,
                    threshold=2000,
                )
            elif (
                metric.metric_id == "data_processing_rate" and metric.value < 100
            ):  # 100 records/second
                await self._create_alert(
                    title="Low Data Processing Rate",
                    description=f"Data processing rate is {metric.value} records/second, below expected performance",
                    level=AlertLevel.MEDIUM,
                    source="application_monitoring",
                    metric=metric.metric_id,
                    current_value=metric.value,
                    threshold=100,
                )

    async def _check_network_alerts(self, metrics: List[MetricData]):
        """Check network metrics for anomalies"""
        # Implementation for network alert checking
        pass

    async def _check_security_alerts(self, metrics: List[MetricData]):
        """Check security metrics for threats"""
        for metric in metrics:
            if metric.metric_id == "failed_login_attempts" and metric.value > 10:
                await self._create_alert(
                    title="Multiple Failed Login Attempts",
                    description=f"Detected {metric.value} failed login attempts, possible brute force attack",
                    level=AlertLevel.HIGH,
                    source="security_monitoring",
                    metric=metric.metric_id,
                    current_value=metric.value,
                    threshold=10,
                )

    async def _create_alert(
        self,
        title: str,
        description: str,
        level: AlertLevel,
        source: str,
        metric: str,
        current_value: float,
        threshold: float,
    ):
        """Create a new alert"""
        alert_id = f"ALERT_{uuid.uuid4().hex[:8]}"

        alert = Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            level=level,
            source=source,
            metric=metric,
            current_value=current_value,
            threshold=threshold,
            timestamp=datetime.now(),
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        self.logger.warning(
            f"🚨 Alert Created: {title} | Level: {level.value} | Value: {current_value}"
        )

    async def _process_active_alerts(self):
        """Process and manage active alerts"""
        current_time = datetime.now()
        alerts_to_resolve = []

        for alert_id, alert in self.active_alerts.items():
            # Check if alert conditions are still met
            recent_metrics = list(self.metrics_store.get(alert.metric, []))[
                -10:
            ]  # Last 10 metrics
            if recent_metrics:
                current_metric = recent_metrics[-1]
                if current_metric.value <= alert.threshold * 0.8:  # 20% below threshold
                    alert.resolved = True
                    alert.resolution_time = current_time
                    alerts_to_resolve.append(alert_id)

                    self.logger.info(f"✅ Alert Resolved: {alert.title}")

        # Remove resolved alerts
        for alert_id in alerts_to_resolve:
            self.active_alerts.pop(alert_id, None)

    async def _send_alert_notifications(self):
        """Send notifications for critical alerts"""
        for alert in self.active_alerts.values():
            if (
                alert.level in [AlertLevel.CRITICAL, AlertLevel.HIGH]
                and not alert.acknowledged
            ):
                await self._send_notification(alert)

    async def _send_notification(self, alert: Alert):
        """Send alert notification through configured channels"""
        notification_message = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description,
            "level": alert.level.value,
            "source": alert.source,
            "metric": alert.metric,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "timestamp": alert.timestamp.isoformat(),
        }

        # Send to configured notification channels
        for channel in self.config["notifications"]["channels"]:
            try:
                if channel == "email":
                    await self._send_email_notification(notification_message)
                elif channel == "slack":
                    await self._send_slack_notification(notification_message)
                elif channel == "webhook":
                    await self._send_webhook_notification(notification_message)
            except Exception as e:
                self.logger.error(f"❌ Notification failed for channel {channel}: {e}")

    async def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status"""
        try:
            # Collect current metrics
            system_metrics = await self._collect_system_metrics()
            app_metrics = await self._collect_application_metrics()

            # Calculate component status
            component_status = await self._calculate_component_health(
                system_metrics, app_metrics
            )

            # Calculate overall status
            overall_status = await self._calculate_overall_health(component_status)

            # Generate recommendations
            recommendations = await self._generate_health_recommendations(
                component_status
            )

            # Prepare metrics summary
            metrics_summary = {
                metric.metric_id: metric.value
                for metric in system_metrics + app_metrics
            }

            return SystemHealth(
                overall_status=overall_status,
                component_status=component_status,
                metrics=metrics_summary,
                last_updated=datetime.now(),
                recommendations=recommendations,
            )

        except Exception as e:
            self.logger.error(f"❌ System health check failed: {e}")
            return SystemHealth(
                overall_status=HealthStatus.UNHEALTHY,
                component_status={},
                metrics={},
                last_updated=datetime.now(),
                recommendations=["Health check system is experiencing issues"],
            )

    async def get_performance_report(self, time_range: str = "1h") -> PerformanceReport:
        """Generate performance analysis report"""
        try:
            report_id = f"REPORT_{uuid.uuid4().hex[:8]}"

            # Calculate time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)  # Default to 1 hour

            # Analyze performance
            analysis_results = await self.performance_analyzer.analyze_performance(
                self.metrics_store, start_time, end_time
            )

            # Detect bottlenecks
            bottlenecks = await self._identify_performance_bottlenecks(analysis_results)

            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                bottlenecks
            )

            # Calculate performance score
            performance_score = await self._calculate_performance_score(
                analysis_results
            )

            # Identify trends
            trends = await self._identify_performance_trends(analysis_results)

            return PerformanceReport(
                report_id=report_id,
                period_start=start_time,
                period_end=end_time,
                metrics_analyzed=analysis_results.get("metrics_analyzed", 0),
                performance_score=performance_score,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                trends=trends,
            )

        except Exception as e:
            self.logger.error(f"❌ Performance report generation failed: {e}")
            raise

    async def get_metrics_data(
        self, metric_id: str, time_range: str = "1h"
    ) -> List[MetricData]:
        """Get metric data for a specific time range"""
        try:
            # Calculate time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)

            # Filter metrics by time range
            metrics = self.metrics_store.get(metric_id, [])
            filtered_metrics = [
                metric
                for metric in metrics
                if start_time <= metric.timestamp <= end_time
            ]

            return filtered_metrics

        except Exception as e:
            self.logger.error(f"❌ Metrics data retrieval failed: {e}")
            return []

    async def create_custom_monitor(self, monitor_config: Dict) -> str:
        """Create a custom monitor with specific rules"""
        try:
            monitor_id = f"MONITOR_{uuid.uuid4().hex[:8]}"

            # Validate monitor configuration
            validation_result = await self._validate_monitor_config(monitor_config)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Monitor configuration invalid: {validation_result['errors']}"
                )

            # Register monitor
            await self._register_custom_monitor(monitor_id, monitor_config)

            self.logger.info(
                f"🔧 Custom Monitor Created: {monitor_id} | Type: {monitor_config.get('type')}"
            )

            return monitor_id

        except Exception as e:
            self.logger.error(f"❌ Custom monitor creation failed: {e}")
            raise

    async def set_alert_rule(self, rule_config: Dict) -> str:
        """Set a custom alert rule"""
        try:
            rule_id = f"RULE_{uuid.uuid4().hex[:8]}"

            # Validate rule configuration
            validation_result = await self._validate_alert_rule(rule_config)
            if not validation_result["valid"]:
                raise ValueError(f"Alert rule invalid: {validation_result['errors']}")

            # Register alert rule
            self.alert_rules[rule_id] = rule_config

            self.logger.info(
                f"⚡ Alert Rule Set: {rule_id} | Metric: {rule_config.get('metric')}"
            )

            return rule_id

        except Exception as e:
            self.logger.error(f"❌ Alert rule setting failed: {e}")
            raise

    # Helper Methods
    async def _perform_health_checks(self) -> SystemHealth:
        """Perform comprehensive health checks"""
        return await self.get_system_health()

    async def _update_health_status(self, health_status: SystemHealth):
        """Update system health status"""
        # Implementation for health status updates
        pass

    async def _generate_health_report(self, health_status: SystemHealth):
        """Generate health report for degraded systems"""
        # Implementation for health reporting
        pass

    async def _analyze_performance_trends(self):
        """Analyze performance trends"""
        # Implementation for trend analysis
        pass

    async def _detect_performance_anomalies(self):
        """Detect performance anomalies"""
        # Implementation for anomaly detection
        pass

    async def _generate_performance_insights(self):
        """Generate performance insights"""
        # Implementation for insight generation
        pass

    async def _cleanup_old_alerts(self):
        """Clean up old alerts from history"""
        cutoff_time = datetime.now() - timedelta(days=7)
        self.alert_history = deque(
            [alert for alert in self.alert_history if alert.timestamp > cutoff_time],
            maxlen=5000,
        )

    async def _calculate_component_health(
        self, system_metrics: List[MetricData], app_metrics: List[MetricData]
    ) -> Dict[str, HealthStatus]:
        """Calculate health status for each component"""
        component_status = {}

        # System components
        cpu_metrics = [m for m in system_metrics if m.metric_id == "cpu_usage"]
        if cpu_metrics:
            cpu_usage = cpu_metrics[-1].value
            component_status["cpu"] = (
                HealthStatus.CRITICAL
                if cpu_usage > 95
                else (
                    HealthStatus.UNHEALTHY
                    if cpu_usage > 85
                    else (
                        HealthStatus.DEGRADED
                        if cpu_usage > 75
                        else HealthStatus.HEALTHY
                    )
                )
            )

        memory_metrics = [m for m in system_metrics if m.metric_id == "memory_usage"]
        if memory_metrics:
            memory_usage = memory_metrics[-1].value
            component_status["memory"] = (
                HealthStatus.CRITICAL
                if memory_usage > 95
                else (
                    HealthStatus.UNHEALTHY
                    if memory_usage > 90
                    else (
                        HealthStatus.DEGRADED
                        if memory_usage > 80
                        else HealthStatus.HEALTHY
                    )
                )
            )

        # Application components
        response_metrics = [
            m for m in app_metrics if m.metric_id == "api_response_time"
        ]
        if response_metrics:
            response_time = response_metrics[-1].value
            component_status["api"] = (
                HealthStatus.UNHEALTHY
                if response_time > 5000
                else (
                    HealthStatus.DEGRADED
                    if response_time > 2000
                    else HealthStatus.HEALTHY
                )
            )

        return component_status

    async def _calculate_overall_health(
        self, component_status: Dict[str, HealthStatus]
    ) -> HealthStatus:
        """Calculate overall system health status"""
        if not component_status:
            return HealthStatus.UNHEALTHY

        status_priority = {
            HealthStatus.CRITICAL: 4,
            HealthStatus.UNHEALTHY: 3,
            HealthStatus.DEGRADED: 2,
            HealthStatus.HEALTHY: 1,
        }

        # Get the worst status
        worst_status = max(component_status.values(), key=lambda x: status_priority[x])
        return worst_status

    async def _generate_health_recommendations(
        self, component_status: Dict[str, HealthStatus]
    ) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []

        for component, status in component_status.items():
            if status != HealthStatus.HEALTHY:
                if component == "cpu" and status in [
                    HealthStatus.UNHEALTHY,
                    HealthStatus.CRITICAL,
                ]:
                    recommendations.append(
                        "Consider optimizing CPU-intensive processes or scaling resources"
                    )
                elif component == "memory" and status in [
                    HealthStatus.UNHEALTHY,
                    HealthStatus.CRITICAL,
                ]:
                    recommendations.append(
                        "Investigate memory leaks or consider adding more RAM"
                    )
                elif component == "api" and status != HealthStatus.HEALTHY:
                    recommendations.append(
                        "Optimize API endpoints and consider load balancing"
                    )

        return recommendations

    async def _identify_performance_bottlenecks(
        self, analysis_results: Dict
    ) -> List[Dict]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Analyze CPU bottlenecks
        cpu_metrics = list(self.metrics_store.get("cpu_usage", []))
        if cpu_metrics and statistics.mean([m.value for m in cpu_metrics[-10:]]) > 80:
            bottlenecks.append(
                {
                    "component": "cpu",
                    "severity": "high",
                    "description": "High CPU usage detected",
                    "impact": "Reduced system responsiveness",
                    "suggestion": "Optimize CPU-intensive processes",
                }
            )

        # Analyze memory bottlenecks
        memory_metrics = list(self.metrics_store.get("memory_usage", []))
        if (
            memory_metrics
            and statistics.mean([m.value for m in memory_metrics[-10:]]) > 85
        ):
            bottlenecks.append(
                {
                    "component": "memory",
                    "severity": "high",
                    "description": "High memory usage detected",
                    "impact": "Potential system instability",
                    "suggestion": "Investigate memory leaks and consider adding RAM",
                }
            )

        return bottlenecks

    async def _generate_performance_recommendations(
        self, bottlenecks: List[Dict]
    ) -> List[Dict]:
        """Generate performance improvement recommendations"""
        recommendations = []

        for bottleneck in bottlenecks:
            if bottleneck["component"] == "cpu":
                recommendations.append(
                    {
                        "priority": (
                            "high" if bottleneck["severity"] == "high" else "medium"
                        ),
                        "action": "CPU Optimization",
                        "description": bottleneck["suggestion"],
                        "estimated_impact": "20-30% performance improvement",
                        "implementation_complexity": "medium",
                    }
                )
            elif bottleneck["component"] == "memory":
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "Memory Management",
                        "description": bottleneck["suggestion"],
                        "estimated_impact": "Improved system stability",
                        "implementation_complexity": "high",
                    }
                )

        return recommendations

    async def _calculate_performance_score(self, analysis_results: Dict) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0

        # Deduct points for issues
        cpu_metrics = list(self.metrics_store.get("cpu_usage", []))
        if cpu_metrics:
            avg_cpu = statistics.mean([m.value for m in cpu_metrics[-10:]])
            if avg_cpu > 80:
                score -= 20
            elif avg_cpu > 60:
                score -= 10

        memory_metrics = list(self.metrics_store.get("memory_usage", []))
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics[-10:]])
            if avg_memory > 85:
                score -= 25
            elif avg_memory > 70:
                score -= 10

        return max(0.0, score)

    async def _identify_performance_trends(
        self, analysis_results: Dict
    ) -> Dict[str, Any]:
        """Identify performance trends"""
        trends = {}

        # CPU trend
        cpu_metrics = list(self.metrics_store.get("cpu_usage", []))
        if len(cpu_metrics) >= 10:
            recent_avg = statistics.mean([m.value for m in cpu_metrics[-5:]])
            previous_avg = statistics.mean([m.value for m in cpu_metrics[-10:-5]])
            trends["cpu_trend"] = (
                "increasing" if recent_avg > previous_avg else "decreasing"
            )

        return trends

    async def _validate_monitor_config(self, config: Dict) -> Dict:
        """Validate monitor configuration"""
        errors = []

        required_fields = ["name", "type", "metric", "threshold"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        return {"valid": len(errors) == 0, "errors": errors}

    async def _validate_alert_rule(self, config: Dict) -> Dict:
        """Validate alert rule configuration"""
        errors = []

        required_fields = ["metric", "condition", "threshold"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        return {"valid": len(errors) == 0, "errors": errors}

    async def _register_custom_monitor(self, monitor_id: str, config: Dict):
        """Register a custom monitor"""
        # Implementation for custom monitor registration
        pass

    # Utility methods for metric collection
    def _measure_api_response_time(self) -> float:
        """Measure API response time"""
        # Implementation for API response time measurement
        return 150.0  # Mock value

    def _calculate_processing_rate(self) -> float:
        """Calculate data processing rate"""
        # Implementation for processing rate calculation
        return 250.0  # Mock value

    def _count_failed_logins(self) -> int:
        """Count failed login attempts"""
        # Implementation for failed login counting
        return 0  # Mock value

    def _count_intrusion_attempts(self) -> int:
        """Count intrusion attempts"""
        # Implementation for intrusion attempt counting
        return 0  # Mock value

    def _count_firewall_blocks(self) -> int:
        """Count firewall blocks"""
        # Implementation for firewall block counting
        return 0  # Mock value

    async def _send_email_notification(self, message: Dict):
        """Send email notification"""
        # Implementation for email notifications
        pass

    async def _send_slack_notification(self, message: Dict):
        """Send Slack notification"""
        # Implementation for Slack notifications
        pass

    async def _send_webhook_notification(self, message: Dict):
        """Send webhook notification"""
        # Implementation for webhook notifications
        pass

    async def shutdown(self):
        """Shutdown monitoring system gracefully"""
        self.logger.info("🛑 Shutting down Monitoring System...")
        self.is_monitoring = False

        # Stop all monitoring threads
        for thread in self.monitoring_threads.values():
            thread.join(timeout=5)

        # Save monitoring state
        await self._save_monitoring_state()

        self.logger.info("✅ Monitoring System shutdown complete")

    async def _save_monitoring_state(self):
        """Save monitoring system state"""
        # Implementation for state saving
        pass


# Supporting Classes


class PerformanceAnalyzer:
    """Performance analysis engine"""

    async def analyze_performance(
        self, metrics_store: Dict, start_time: datetime, end_time: datetime
    ) -> Dict:
        """Analyze system performance"""
        return {"metrics_analyzed": len(metrics_store), "analysis_complete": True}


class AnomalyDetectionEngine:
    """Anomaly detection engine"""

    async def detect_anomalies(self, metrics: List[MetricData]) -> List[Dict]:
        """Detect anomalies in metrics"""
        return []


class DashboardManager:
    """Monitoring dashboard manager"""

    async def update_dashboard(self, metrics: List[MetricData]):
        """Update monitoring dashboard"""
        pass


class ReportGenerator:
    """Report generation engine"""

    async def generate_report(self, report_data: Dict) -> str:
        """Generate monitoring report"""
        return "report_generated"


class PrometheusExporter:
    """Prometheus metrics exporter"""

    def __init__(self):
        self.metrics = {}

    async def update_metric(self, metric: MetricData):
        """Update Prometheus metric"""
        if metric.metric_id not in self.metrics:
            self.metrics[metric.metric_id] = Gauge(metric.metric_id, metric.name)

        self.metrics[metric.metric_id].set(metric.value)


# Usage Example
async def demo_monitoring_system():
    """Demonstrate the advanced monitoring system"""
    monitoring_system = AdvancedMonitoringSystem()

    try:
        # Start monitoring system
        await monitoring_system.start_monitoring()

        # Get system health
        health_status = await monitoring_system.get_system_health()
        print(f"System Health: {health_status.overall_status.value}")

        # Get performance report
        performance_report = await monitoring_system.get_performance_report("1h")
        print(f"Performance Score: {performance_report.performance_score}")

        # Create custom monitor
        custom_monitor = {
            "name": "High CPU Monitor",
            "type": "threshold",
            "metric": "cpu_usage",
            "threshold": 90.0,
            "action": "alert",
        }
        monitor_id = await monitoring_system.create_custom_monitor(custom_monitor)
        print(f"Custom Monitor Created: {monitor_id}")

        # Keep running for demo
        await asyncio.sleep(30)

    finally:
        await monitoring_system.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_monitoring_system())
