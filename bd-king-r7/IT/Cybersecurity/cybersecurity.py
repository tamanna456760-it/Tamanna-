# LEGITIMATE security learning tools
import hashlib
import socket
import ssl

class SecurityEducation:
    def __init__(self):
        self.authorized_targets = []
    
    def hash_analysis(self, file_path):
        """Learn about file hashing for integrity checking"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            md5_hash = hashlib.md5(file_data).hexdigest()
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            
            return {
                'md5': md5_hash,
                'sha256': sha256_hash,
                'file_size': len(file_data)
            }
        except FileNotFoundError:
            return "File not found"
    
    def port_scanner_educational(self, host, ports):
        """Educational port scanning - ONLY for systems you own"""
        results = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    results[port] = "Open"
                else:
                    results[port] = "Closed"
                sock.close()
            except Exception as e:
                results[port] = f"Error: {e}"
        return results