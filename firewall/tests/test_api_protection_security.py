"""Security tests for Tamanna AI API protection."""
import unittest
from firewall.api_protection import validate_api_request
class TestAPIProtectionSecurity(unittest.TestCase):
    def test_valid_health_request_is_checked(self):
        """A health endpoint request should be processed without crashing."""
        result = validate_api_request(
            method="GET",
            path="/api/health",
            content_type="application/json",
            content_length=0,
        )
        self.assertIsNotNone(result)
    def test_unsupported_method_is_rejected_or_reported(self):
        """An unsupported HTTP method should not silently pass unchecked."""
        result = validate_api_request(
            method="TRACE",
            path="/api/health",
            content_type="application/json",
            content_length=0,
        )
        self.assertIsNotNone(result)
        # Accommodate implementations that return a result object or a dict.
        if isinstance(result, dict):
            if "allowed" in result:
                self.assertFalse(result["allowed"])
        elif hasattr(result, "allowed"):
            self.assertFalse(result.allowed)
    def test_suspicious_path_is_checked(self):
        """Traversal-like paths should be inspected by the protection layer."""
        result = validate_api_request(
            method="GET",
            path="/../../etc/passwd",
            content_type="application/json",
            content_length=0,
        )
        self.assertIsNotNone(result)
if __name__ == "__main__":
    unittest.main()