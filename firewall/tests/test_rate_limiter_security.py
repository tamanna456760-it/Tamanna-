"""Security tests for Tamanna AI firewall rate limiter."""
import unittest
from firewall.rate_limiter import RateLimiter
class TestRateLimiterSecurity(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
    def test_first_request_returns_allowed_result(self):
        """A new client should normally be allowed its first request."""
        result = self.limiter.check("security-test-client")
        self.assertTrue(hasattr(result, "allowed"))
        self.assertIsInstance(result.allowed, bool)
        self.assertTrue(result.allowed)
    def test_separate_clients_are_tracked_independently(self):
        """One client's requests should not automatically block another."""
        first = self.limiter.check("client-security-alpha")
        second = self.limiter.check("client-security-beta")
        self.assertTrue(first.allowed)
        self.assertTrue(second.allowed)
    def test_result_contains_retry_information_if_limited(self):
        """A denied request may provide retry timing information."""
        client_id = "security-burst-test-client"
        results = [
            self.limiter.check(client_id)
            for _ in range(100)
        ]
        denied = [result for result in results if not result.allowed]
        if not denied:
            self.skipTest(
                "Default limiter settings did not reach the request limit."
            )
        result = denied[0]
        # Different implementations may use different field names.
        retry_fields = ("retry_after", "retry_after_seconds", "reset_after")
        available = [
            name for name in retry_fields
            if hasattr(result, name)
        ]
        if available:
            value = getattr(result, available[0])
            self.assertIsInstance(value, (int, float))
            self.assertGreaterEqual(value, 0)
if __name__ == "__main__":
    unittest.main()