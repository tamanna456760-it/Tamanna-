"""
Tamanna AI — API Protection Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_api_protection -v
These tests use local request metadata only.
They do not send network requests or change firewall rules.
"""
import unittest
from firewall.api_protection import (
    DEFAULT_MAX_BODY_BYTES,
    get_trusted_client_id,
    is_protected_path,
    validate_api_request,
)
class TestRequestMethods(unittest.TestCase):
    def test_get_request_is_allowed(self):
        result = validate_api_request(
            method="GET",
            path="/api/chat",
        )
        self.assertTrue(result.allowed)
    def test_method_is_case_insensitive(self):
        result = validate_api_request(
            method="get",
            path="/api/chat",
        )
        self.assertTrue(result.allowed)
    def test_trace_method_is_rejected(self):
        result = validate_api_request(
            method="TRACE",
            path="/api/chat",
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 405)
class TestRequestPaths(unittest.TestCase):
    def test_normal_api_path(self):
        result = validate_api_request(
            method="GET",
            path="/api/chat",
        )
        self.assertTrue(result.allowed)
    def test_path_traversal_is_rejected(self):
        result = validate_api_request(
            method="GET",
            path="/api/../admin",
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "invalid_path")
    def test_backslash_is_rejected(self):
        result = validate_api_request(
            method="GET",
            path=r"/api\admin",
        )
        self.assertFalse(result.allowed)
    def test_empty_path_is_rejected(self):
        result = validate_api_request(
            method="GET",
            path="",
        )
        self.assertFalse(result.allowed)
    def test_sensitive_path_requires_authentication(self):
        result = validate_api_request(
            method="GET",
            path="/api/admin/status",
            authenticated=False,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 401)
    def test_authenticated_sensitive_path_passes_auth_check(self):
        result = validate_api_request(
            method="GET",
            path="/api/admin/status",
            authenticated=True,
        )
        self.assertTrue(result.allowed)
class TestRequestBody(unittest.TestCase):
    def test_body_under_limit_is_allowed(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="application/json",
            content_length=100,
        )
        self.assertTrue(result.allowed)
    def test_body_over_limit_is_rejected(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="application/json",
            content_length=DEFAULT_MAX_BODY_BYTES + 1,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 413)
    def test_negative_content_length_is_rejected(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="application/json",
            content_length=-1,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 400)
    def test_json_endpoint_rejects_wrong_content_type(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="text/plain",
            content_length=10,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 415)
    def test_json_content_type_with_charset_is_allowed(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="application/json; charset=utf-8",
            content_length=10,
        )
        self.assertTrue(result.allowed)
class TestProtectedPaths(unittest.TestCase):
    def test_admin_path_is_protected(self):
        self.assertTrue(is_protected_path("/api/admin"))
    def test_admin_subpath_is_protected(self):
        self.assertTrue(is_protected_path("/api/admin/users"))
    def test_similar_unrelated_path_is_not_protected(self):
        self.assertFalse(is_protected_path("/api/administrator"))
class TestTrustedClientIdentity(unittest.TestCase):
    def test_direct_client_host_is_returned(self):
        self.assertEqual(
            get_trusted_client_id(direct_client_host="127.0.0.1"),
            "127.0.0.1",
        )
    def test_missing_client_host_is_rejected(self):
        self.assertIsNone(
            get_trusted_client_id(direct_client_host=None)
        )
    def test_newline_in_client_host_is_rejected(self):
        self.assertIsNone(
            get_trusted_client_id(
                direct_client_host="127.0.0.1\nforged"
            )
        )
class TestResultFormat(unittest.TestCase):
    def test_result_dictionary_has_expected_fields(self):
        result = validate_api_request(
            method="GET",
            path="/api/chat",
        ).to_dict()
        self.assertEqual(
            set(result.keys()),
            {"allowed", "status_code", "code", "message"},
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)