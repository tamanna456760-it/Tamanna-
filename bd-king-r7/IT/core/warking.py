# Example structure for power system testing
class PowerHABTest:
    def __init__(self):
        self.test_results = {}
        
    def voltage_test(self, expected_voltage, tolerance=0.05):
        """Test voltage levels within tolerance"""
        actual_voltage = self.read_voltage()
        within_range = abs(actual_voltage - expected_voltage) <= expected_voltage * tolerance
        self.test_results['voltage'] = within_range
        return within_range
    
    def current_test(self, max_current):
        """Test current draw doesn't exceed maximum"""
        actual_current = self.read_current()
        within_limit = actual_current <= max_current
        self.test_results['current'] = within_limit
        return within_limit
    
    def power_cycle_test(self, cycles=3):
        """Test multiple power cycles"""
        for i in range(cycles):
            if not self.single_power_cycle():
                return False
        return True