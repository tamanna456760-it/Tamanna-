#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security & Network Monitoring Module
Detects ARP spoofing, suspicious IPs, and malicious activity
"""

import json
import time
import threading
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Monitors network security and blocks threats"""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path('config/security_config.json')
        self.blacklist: Dict[str, str] = {}  # IP -> Expected MAC
        self.whitelist: Set[str] = set()
        self.blocked_ips: Dict[str, float] = {}  # IP -> block_time
        self.alerts: List[Dict] = []
        self.rate_limit_seconds = 60
        self.is_running = False
        
        self.load_config()
    
    def load_config(self):
        """Load security configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.blacklist = config.get('blacklist', {})
                    self.whitelist = set(config.get('whitelist', []))
                    self.rate_limit_seconds = config.get('rate_limit_seconds', 60)
                logger.info("Security config loaded")
            except Exception as e:
                logger.error(f"Failed to load security config: {e}")
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default security configuration"""
        default_config = {
            'blacklist': {},
            'whitelist': ['127.0.0.1'],
            'rate_limit_seconds': 60,
            'enable_arp_monitoring': True,
            'enable_port_scanning': True,
            'alert_methods': ['log', 'email']
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
    
    def add_to_blacklist(self, ip: str, expected_mac: str):
        """Add IP to blacklist"""
        self.blacklist[ip] = expected_mac.upper()
        logger.info(f"Added to blacklist: {ip} -> {expected_mac}")
    
    def add_to_whitelist(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip)
        logger.info(f"Added to whitelist: {ip}")
    
    def is_threat(self, ip: str, mac: str) -> tuple:
        """Check if IP/MAC combination is a threat
        
        Returns:
            (is_threat, threat_type, severity)
        """
        # Check whitelist
        if ip in self.whitelist:
            return False, None, 'none'
        
        # Check blacklist for MAC spoofing
        if ip in self.blacklist:
            expected_mac = self.blacklist[ip]
            if mac.upper() != expected_mac.upper():
                return True, 'arp_spoofing', 'critical'
            return True, 'blacklisted_ip', 'warning'
        
        return False, None, 'none'
    
    def block_ip(self, ip: str, reason: str = 'security_threat') -> bool:
        """Block IP address using firewall"""
        now = time.time()
        
        # Rate limiting
        if ip in self.blocked_ips:
            if now - self.blocked_ips[ip] < self.rate_limit_seconds:
                logger.debug(f"Rate limit: IP {ip} already blocked recently")
                return False
        
        try:
            # Try UFW first
            subprocess.run(
                ['sudo', 'ufw', 'deny', 'from', ip],
                capture_output=True,
                timeout=5
            )
            
            self.blocked_ips[ip] = now
            logger.warning(f"Blocked IP: {ip} (reason: {reason})")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"Firewall command timeout for {ip}")
            return False
        except Exception as e:
            logger.error(f"Failed to block IP {ip}: {e}")
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock IP address"""
        try:
            subprocess.run(
                ['sudo', 'ufw', 'delete', 'deny', 'from', ip],
                capture_output=True,
                timeout=5
            )
            
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
            
            logger.info(f"Unblocked IP: {ip}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unblock IP {ip}: {e}")
            return False
    
    def create_alert(self, ip: str, mac: str, threat_type: str, severity: str):
        """Create security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'mac': mac,
            'threat_type': threat_type,
            'severity': severity,
            'action_taken': 'ip_blocked' if threat_type == 'arp_spoofing' else 'alert_logged'
        }
        
        self.alerts.append(alert)
        logger.critical(f"SECURITY ALERT: {threat_type} detected from {ip} ({mac})")
        
        return alert
    
    def get_blocked_ips(self) -> Dict[str, float]:
        """Get list of blocked IPs"""
        return self.blocked_ips.copy()
    
    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """Get security alerts"""
        return self.alerts[-limit:]
    
    def save_state(self, output_file: Path = None):
        """Save security state to file"""
        if output_file is None:
            output_file = Path('reports/security_state.json')
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'timestamp': datetime.now().isoformat(),
            'blocked_ips': self.blocked_ips,
            'alerts_count': len(self.alerts),
            'recent_alerts': self.alerts[-10:]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info(f"Security state saved to {output_file}")
        return output_file


class ARPMonitor:
    """ARP spoofing detection using packet sniffing"""
    
    def __init__(self, security_monitor: SecurityMonitor):
        self.security_monitor = security_monitor
        self.is_running = False
        self.packets_processed = 0
        
        # Try to import scapy
        try:
            from scapy.all import sniff, ARP
            self.sniff = sniff
            self.ARP = ARP
            self.scapy_available = True
        except ImportError:
            logger.warning("Scapy not installed. ARP monitoring disabled.")
            self.scapy_available = False
    
    def handle_arp_packet(self, packet):
        """Handle incoming ARP packet"""
        if not self.scapy_available:
            return
        
        try:
            if self.ARP in packet and packet[self.ARP].op == 2:  # ARP reply
                ip = packet[self.ARP].psrc
                mac = packet[self.ARP].hwsrc
                
                self.packets_processed += 1
                
                # Check for threats
                is_threat, threat_type, severity = self.security_monitor.is_threat(ip, mac)
                
                if is_threat:
                    # Create alert
                    self.security_monitor.create_alert(ip, mac, threat_type, severity)
                    
                    # Block if critical
                    if severity == 'critical':
                        self.security_monitor.block_ip(ip, f"ARP {threat_type}")
        
        except Exception as e:
            logger.error(f"Error processing ARP packet: {e}")
    
    def start_monitoring(self, interface: Optional[str] = None):
        """Start ARP spoofing monitoring"""
        if not self.scapy_available:
            logger.error("Cannot start ARP monitoring: Scapy not available")
            return False
        
        self.is_running = True
        logger.info(f"Starting ARP monitoring on interface {interface or 'all'}")
        
        try:
            self.sniff(
                filter="arp",
                store=False,
                prn=self.handle_arp_packet,
                stop_filter=lambda x: not self.is_running
            )
            return True
        except Exception as e:
            logger.error(f"ARP monitoring error: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop ARP monitoring"""
        self.is_running = False
        logger.info(f"ARP monitoring stopped. Packets processed: {self.packets_processed}")
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        return {
            'is_running': self.is_running,
            'packets_processed': self.packets_processed,
            'blocked_ips_count': len(self.security_monitor.blocked_ips),
            'alerts_count': len(self.security_monitor.alerts)
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize security monitor
    security = SecurityMonitor()
    
    # Add blacklist entries
    security.add_to_blacklist('192.168.1.100', 'AA:BB:CC:DD:EE:FF')
    
    # Start ARP monitoring
    arp_monitor = ARPMonitor(security)
    # arp_monitor.start_monitoring()  # Requires scapy and root privileges
    
    print("Security monitoring active")
