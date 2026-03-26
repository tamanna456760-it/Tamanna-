# network_security_monitor.py
import socket
import subprocess
import time
import json
import logging
from collections import defaultdict, deque
from datetime import datetime
import threading
from typing import Dict, List, Set
import psutil

class EnhancedNetworkSecurityMonitor:
    """
    Comprehensive network security monitoring for legitimate security auditing
    Only use on systems you own or have explicit permission to monitor
    """
    
    def __init__(self, config_file="security_config.json"):
        self.config = self._load_config(config_file)
        self.setup_logging()
        
        # Monitoring data structures
        self.connection_history = defaultdict(deque)
        self.port_scan_alerts = []
        self.suspicious_activity = []
        
        # Known safe IPs and ports
        self.whitelist_ips = set(self.config.get('whitelist_ips', []))
        self.allowed_ports = set(self.config.get('allowed_ports', [80, 443, 22, 21, 53]))
        
        # Rate limiting
        self.connection_attempts = defaultdict(int)
        self.last_reset = time.time()
    
    def _load_config(self, config_file):
        """Load security configuration"""
        default_config = {
            'whitelist_ips': ['127.0.0.1', '::1'],
            'allowed_ports': [80, 443, 22, 21, 53, 25, 110, 993],
            'scan_interval': 60,
            'max_connection_attempts': 10,
            'alert_threshold': 5
        }
        
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            print(f"Config file {config_file} not found, using defaults")
        
        return default_config
    
    def setup_logging(self):
        """Setup logging for security events"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def port_scan_detection(self, target_ip="127.0.0.1", ports_to_scan=None):
        """
        Security-focused port scanning for vulnerability assessment
        """
        if ports_to_scan is None:
            ports_to_scan = list(range(1, 1025))  # Well-known ports
        
        open_ports = []
        security_risks = []
        
        self.logger.info(f"Starting security port scan on {target_ip}")
        
        for port in ports_to_scan:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    result = sock.connect_ex((target_ip, port))
                    
                    if result == 0:
                        # Port is open
                        service_info = self._get_service_info(port)
                        risk_level = self._assess_port_risk(port)
                        
                        open_ports.append({
                            'port': port,
                            'service': service_info,
                            'risk_level': risk_level,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        if risk_level == "HIGH":
                            security_risks.append(port)
                            self.logger.warning(f"HIGH RISK: Port {port} ({service_info}) is open")
                        
            except Exception as e:
                continue
        
        return {
            'open_ports': open_ports,
            'security_risks': security_risks,
            'scan_timestamp': datetime.now().isoformat(),
            'target_ip': target_ip
        }
    
    def _get_service_info(self, port):
        """Get common service information for a port"""
        common_services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 443: "HTTPS",
            1433: "MSSQL", 3306: "MySQL", 3389: "RDP",
            5432: "PostgreSQL", 5900: "VNC", 6379: "Redis"
        }
        return common_services.get(port, "Unknown")
    
    def _assess_port_risk(self, port):
        """Assess security risk level for an open port"""
        high_risk_ports = {21, 23, 1433, 3389, 5900}  # FTP, Telnet, MSSQL, RDP, VNC
        medium_risk_ports = {22, 25, 110, 5432, 6379}  # SSH, SMTP, POP3, PostgreSQL, Redis
        
        if port in high_risk_ports:
            return "HIGH"
        elif port in medium_risk_ports:
            return "MEDIUM"
        elif port in self.allowed_ports:
            return "LOW"
        else:
            return "UNKNOWN"
    
    def monitor_network_connections(self):
        """Monitor active network connections for suspicious activity"""
        try:
            connections = psutil.net_connections()
            suspicious_connections = []
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    conn_info = self._analyze_connection(conn)
                    if conn_info['suspicious']:
                        suspicious_connections.append(conn_info)
                        self.logger.warning(f"Suspicious connection: {conn_info}")
            
            return suspicious_connections
            
        except Exception as e:
            self.logger.error(f"Error monitoring connections: {e}")
            return []
    
    def _analyze_connection(self, conn):
        """Analyze a connection for suspicious characteristics"""
        suspicious = False
        reasons = []
        
        # Check for unusual ports
        if conn.laddr.port > 49151 and conn.raddr:  # Dynamic/private ports
            reasons.append(f"Unusual port: {conn.laddr.port}")
            suspicious = True
        
        # Check for known malicious IP patterns (basic example)
        if conn.raddr:
            remote_ip = conn.raddr.ip
            if self._is_suspicious_ip(remote_ip):
                reasons.append(f"Suspicious remote IP: {remote_ip}")
                suspicious = True
        
        return {
            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
            'status': conn.status,
            'pid': conn.pid,
            'suspicious': suspicious,
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_suspicious_ip(self, ip):
        """Basic suspicious IP detection (expand with threat intelligence)"""
        # Example: Check for private IPs making unexpected connections
        if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
            # Internal IPs are usually fine, but could be lateral movement
            return False
        
        # Add more sophisticated checks here
        # Integration with threat intelligence feeds would go here
        
        return False
    
    def bandwidth_monitoring(self, interval=10):
        """Monitor network bandwidth usage"""
        try:
            stats = psutil.net_io_counters()
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Bandwidth monitoring error: {e}")
            return {}
    
    def continuous_monitoring(self, scan_interval=300):
        """Run continuous security monitoring"""
        self.logger.info("Starting continuous security monitoring")
        
        try:
            while True:
                # Monitor active connections
                suspicious_conns = self.monitor_network_connections()
                if suspicious_conns:
                    self.logger.warning(f"Found {len(suspicious_conns)} suspicious connections")
                
                # Monitor bandwidth
                bandwidth = self.bandwidth_monitoring()
                
                # Periodic port scanning (less frequent)
                if int(time.time()) % scan_interval == 0:
                    scan_results = self.port_scan_detection("127.0.0.1")
                    if scan_results['security_risks']:
                        self.logger.critical(f"Security risks detected: {scan_results['security_risks']}")
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Security monitoring stopped by user")
    
    def generate_security_report(self):
        """Generate a comprehensive security report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'port_scan_results': self.port_scan_detection("127.0.0.1"),
            'current_connections': len(psutil.net_connections()),
            'bandwidth_usage': self.bandwidth_monitoring(),
            'recent_alerts': self.suspicious_activity[-10:]  # Last 10 alerts
        }
        
        # Save report to file
        with open('security_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

# Example configuration file (security_config.json)
SAMPLE_CONFIG = {
    "whitelist_ips": ["127.0.0.1", "::1", "192.168.1.0/24"],
    "allowed_ports": [80, 443, 22, 21, 53, 25, 993, 995],
    "scan_interval": 300,
    "max_connection_attempts": 10,
    "alert_threshold": 5
}

def main():
    """Main function for security monitoring"""
    print("=== Network Security Monitor ===")
    print("For legitimate security auditing only!")
    print("Only use on systems you own or have permission to monitor\n")
    
    # Create sample config if it doesn't exist
    try:
        with open('security_config.json', 'r') as f:
            pass
    except FileNotFoundError:
        with open('security_config.json', 'w') as f:
            json.dump(SAMPLE_CONFIG, f, indent=2)
        print("Created sample security_config.json")
    
    monitor = EnhancedNetworkSecurityMonitor()
    
    while True:
        print("\nSecurity Monitoring Options:")
        print("1. Quick Port Scan")
        print("2. Monitor Network Connections")
        print("3. Generate Security Report")
        print("4. Continuous Monitoring")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            print("\nPerforming security port scan...")
            results = monitor.port_scan_detection("127.0.0.1")
            print(f"Found {len(results['open_ports'])} open ports")
            for port_info in results['open_ports']:
                print(f"Port {port_info['port']}: {port_info['service']} - Risk: {port_info['risk_level']}")
        
        elif choice == '2':
            print("\nMonitoring network connections...")
            suspicious = monitor.monitor_network_connections()
            print(f"Found {len(suspicious)} suspicious connections")
            for conn in suspicious:
                print(f"Suspicious: {conn}")
        
        elif choice == '3':
            print("\nGenerating security report...")
            report = monitor.generate_security_report()
            print("Security report saved to security_report.json")
        
        elif choice == '4':
            print("\nStarting continuous monitoring (Ctrl+C to stop)...")
            try:
                monitor.continuous_monitoring()
            except KeyboardInterrupt:
                print("\nReturning to menu...")
        
        elif choice == '5':
            print("Exiting security monitor.")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()