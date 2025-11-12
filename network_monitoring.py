# network_monitor.py - Legitimate network security monitoring
import socket
import subprocess
import time
from collections import defaultdict

class NetworkSecurityMonitor:
    """Monitor network for security purposes on YOUR OWN systems"""
    
    def __init__(self, allowed_ports=[80, 443, 22, 21]):
        self.allowed_ports = allowed_ports
        self.connection_log = defaultdict(list)
    
    def scan_open_ports(self, target_ip="127.0.0.1"):
        """Scan open ports on YOUR OWN system for security auditing"""
        open_ports = []
        
        for port in range(1, 1025):  # Well-known ports only
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        open_ports.append(port)
                        print(f"Port {port} is open")
            except Exception as e:
                continue
        
        return open_ports
    
    def check_suspicious_connections(self):
        """Check for suspicious network connections"""
        try:
            # Use netstat to check connections (Linux/Unix)
            result = subprocess.run(['netstat', '-tunap'], 
                                  capture_output=True, text=True)
            
            suspicious_conns = []
            for line in result.stdout.split('\n'):
                if 'ESTABLISHED' in line:
                    # Add your own security checks here
                    suspicious_conns.append(line)
            
            return suspicious_conns
        except Exception as e:
            print(f"Error checking connections: {e}")
            return []

# Usage for legitimate security auditing
if __name__ == "__main__":
    monitor = NetworkSecurityMonitor()
    print("Scanning localhost for open ports...")
    open_ports = monitor.scan_open_ports("127.0.0.1")
    print(f"Found {len(open_ports)} open ports")