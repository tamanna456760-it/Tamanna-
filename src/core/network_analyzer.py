#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Analysis & Monitoring Module
Analyzes network traffic, detects anomalies, and identifies threats
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """Analyzes network traffic and detects anomalies"""
    
    def __init__(self):
        self.traffic_stats = defaultdict(lambda: {'packets': 0, 'bytes': 0, 'last_seen': None})
        self.suspicious_patterns = []
        self.port_scans = []
        self.dos_attempts = []
    
    def detect_port_scan(self, source_ip: str, ports: List[int]) -> bool:
        """Detect port scanning activity
        
        Args:
            source_ip: Source IP address
            ports: List of ports being scanned
        
        Returns:
            True if port scan detected
        """
        # Port scan threshold: 10+ different ports in 1 minute
        if len(ports) >= 10:
            self.port_scans.append({
                'timestamp': datetime.now().isoformat(),
                'source_ip': source_ip,
                'ports_scanned': len(ports),
                'ports': ports[:20]  # Store first 20 ports
            })
            logger.warning(f"Port scan detected from {source_ip}: {len(ports)} ports")
            return True
        return False
    
    def detect_dos_attack(self, source_ip: str, packet_count: int, time_window: int = 60) -> bool:
        """Detect DoS (Denial of Service) attacks
        
        Args:
            source_ip: Source IP address
            packet_count: Number of packets
            time_window: Time window in seconds
        
        Returns:
            True if DoS attack detected
        """
        # DoS threshold: 1000+ packets from single IP in 1 minute
        if packet_count >= 1000:
            self.dos_attempts.append({
                'timestamp': datetime.now().isoformat(),
                'source_ip': source_ip,
                'packet_count': packet_count,
                'time_window': time_window
            })
            logger.critical(f"DoS attack detected from {source_ip}: {packet_count} packets in {time_window}s")
            return True
        return False
    
    def detect_suspicious_ports(self, ip: str, port: int) -> bool:
        """Detect connections to suspicious ports
        
        Args:
            ip: IP address
            port: Port number
        
        Returns:
            True if suspicious port detected
        """
        # Common malware/backdoor ports
        suspicious_ports = [135, 139, 445, 1433, 3306, 3389, 5985, 5986, 27017, 27018]
        
        if port in suspicious_ports:
            self.suspicious_patterns.append({
                'timestamp': datetime.now().isoformat(),
                'ip': ip,
                'port': port,
                'threat': 'suspicious_port'
            })
            logger.warning(f"Suspicious port access from {ip}:{port}")
            return True
        return False
    
    def update_traffic_stats(self, ip: str, packets: int = 1, bytes_count: int = 0):
        """Update traffic statistics for an IP"""
        self.traffic_stats[ip]['packets'] += packets
        self.traffic_stats[ip]['bytes'] += bytes_count
        self.traffic_stats[ip]['last_seen'] = datetime.now().isoformat()
    
    def get_traffic_stats(self, ip: Optional[str] = None) -> Dict:
        """Get traffic statistics"""
        if ip:
            return dict(self.traffic_stats.get(ip, {}))
        return dict(self.traffic_stats)
    
    def get_report(self) -> Dict:
        """Generate network analysis report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_ips_monitored': len(self.traffic_stats),
            'port_scans_detected': len(self.port_scans),
            'dos_attempts': len(self.dos_attempts),
            'suspicious_patterns': len(self.suspicious_patterns),
            'recent_port_scans': self.port_scans[-5:],
            'recent_dos_attempts': self.dos_attempts[-5:],
            'recent_suspicious': self.suspicious_patterns[-5:]
        }
    
    def save_report(self, output_file: Path = None):
        """Save analysis report to file"""
        if output_file is None:
            output_file = Path('reports/network_analysis.json')
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_report(), f, indent=2)
        
        logger.info(f"Report saved to {output_file}")
        return output_file


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NetworkAnalyzer()
    print(analyzer.get_report())
