"""Tests for Tamanna AI firewall rate limiter."""
import unittest
from firewall.rate_limiter import RateLimiter
class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
    def test_first_request_is_allowed(self):
        """A new client should normally be allowed its first request."""
        result = self.limiter.check("test-client-first")
        self.assertTrue(hasattr(result, "allowed"))
        self.assertIsInstance(result.allowed, bool)
        self.assertTrue(result.allowed)
    def test_result_has_boolean_allowed_field(self):
        """The limiter should return a result with a boolean allowed field."""
        result = self.limiter.check("test-client-result")
        self.assertIsInstance(result.allowed, bool)
    def test_clients_are_tracked_independently(self):
        """A request from one client should not automatically block another."""
        first = self.limiter.check("client-alpha")
        second = self.limiter.check("client-beta")
        self.assertTrue(first.allowed)
        self.assertTrue(second.allowed)
if __name__ == "__main__":
    unittest.main()