# tamanna/bd-king-r7/it/
# For LEGAL security testing with proper authorization
class AuthorizedPenTest:
    def __init__(self, authorized_scope_file):
        self.load_authorized_scope(authorized_scope_file)
    
    def load_authorized_scope(self, scope_file):
        """Load authorized targets from file"""
        try:
            with open(scope_file, 'r') as f:
                self.authorized_targets = [line.strip() for line in f]
            print(f"Loaded {len(self.authorized_targets)} authorized targets")
        except FileNotFoundError:
            print("No authorization file found")
    
    def is_authorized(self, target):
        """Check if target is in authorized scope"""
        return target in self.authorized_targets
    
    def run_vulnerability_scan(self, target):
        """Run authorized vulnerability scan"""
        if not self.is_authorized(target):
            return "Target not authorized for testing"
        
        # Implement legitimate vulnerability scanning
        # Using tools like nmap, nikto, etc.
        pass