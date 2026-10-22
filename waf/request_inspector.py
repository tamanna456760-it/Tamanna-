"""Tamanna AI WAF request inspection.
Safe initial implementation: inspect request metadata and report
limit violations. This module does not block requests or change
system firewall rules.
"""
from typing import Any, Dict, Mapping, Optional
class RequestInspector:
    """Inspect HTTP request metadata against configured limits."""
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.limits = dict(self.config.get("request_limits", {}))
    @staticmethod
    def _safe_length(value: Any) -> int:
        """Return a safe length for strings and byte sequences."""
        if isinstance(value, (str, bytes, bytearray)):
            return len(value)
        return 0
    def inspect(
        self,
        path: str = "/",
        headers: Optional[Mapping[str, Any]] = None,
        query_parameters: Optional[Mapping[str, Any]] = None,
        body: Any = b"",
    ) -> Dict[str, Any]:
        """Inspect supplied request metadata and return findings."""
        headers = headers or {}
        query_parameters = query_parameters or {}
        findings = []
        max_url = int(self.limits.get("max_url_length", 8192))
        max_headers = int(self.limits.get("max_header_count", 100))
        max_header_value = int(
            self.limits.get("max_header_value_length", 8192)
        )
        max_query_parameters = int(
            self.limits.get("max_query_parameters", 200)
        )
        max_request_size = int(
            self.limits.get("max_request_size_bytes", 1048576)
        )
        if self._safe_length(path) > max_url:
            findings.append({
                "rule": "url_too_long",
                "severity": "medium",
                "reason": "Request path exceeds configured URL length limit.",
            })
        if len(headers) > max_headers:
            findings.append({
                "rule": "too_many_headers",
                "severity": "medium",
                "reason": "Request contains too many headers.",
            })
        for name, value in headers.items():
            if self._safe_length(name) > max_header_value:
                findings.append({
                    "rule": "header_name_too_long",
                    "severity": "medium",
                    "reason": "A header name exceeds the configured limit.",
                })
                break
            if self._safe_length(value) > max_header_value:
                findings.append({
                    "rule": "header_value_too_long",
                    "severity": "medium",
                    "reason": "A header value exceeds the configured limit.",
                })
                break
        if len(query_parameters) > max_query_parameters:
            findings.append({
                "rule": "too_many_query_parameters",
                "severity": "medium",
                "reason": "Request contains too many query parameters.",
            })
        body_size = self._safe_length(body)
        if body_size > max_request_size:
            findings.append({
                "rule": "request_body_too_large",
                "severity": "high",
                "reason": "Request body exceeds the configured size limit.",
            })
        return {
            "project": "Tamanna AI",
            "component": "WAF",
            "mode": self.config.get("mode", "monitor_only"),
            "status": "alert" if findings else "ok",
            "findings": findings,
            "finding_count": len(findings),
            "request_blocked": False,
            "system_firewall_modified": False,
        }