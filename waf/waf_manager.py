"""Tamanna AI WAF manager.
Coordinates request inspection, detection rules, and event logging.
Default behavior is monitor-only with no request blocking.
"""
from typing import Any, Dict, Mapping, Optional
from .event_logger import WAFEventLogger
from .request_inspector import RequestInspector
from .rule_engine import RuleEngine
class WAFManager:
    """Coordinate Tamanna AI WAF inspection components."""
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.enabled = bool(self.config.get("enabled", True))
        self.mode = str(self.config.get("mode", "monitor_only"))
        # This initial implementation intentionally supports monitor-only.
        if self.mode != "monitor_only":
            raise ValueError(
                "This WAF implementation supports monitor_only mode only."
            )
        enforcement = self.config.get("enforcement", {})
        if not isinstance(enforcement, Mapping):
            raise ValueError("WAF enforcement configuration must be an object.")
        if enforcement.get("block_requests", False) is not False:
            raise ValueError(
                "Request blocking must remain disabled in this implementation."
            )
        if enforcement.get("modify_system_firewall", False) is not False:
            raise ValueError(
                "System firewall modification must remain disabled."
            )
        self.inspector = RequestInspector(self.config)
        self.rule_engine = RuleEngine(self.config)
        self.event_logger = WAFEventLogger(self.config)
    def inspect_request(
        self,
        path: str = "/",
        query_string: str = "",
        headers: Optional[Mapping[str, Any]] = None,
        body: Any = b"",
    ) -> Dict[str, Any]:
        """Inspect request metadata and suspicious patterns."""
        if not self.enabled:
            return {
                "project": "Tamanna AI",
                "component": "WAF",
                "mode": self.mode,
                "status": "disabled",
                "findings": [],
                "finding_count": 0,
                "request_blocked": False,
                "system_firewall_modified": False,
            }
        headers = headers or {}
        metadata_result = self.inspector.inspect(
            path=path,
            headers=headers,
            query_parameters=self._parse_query_parameters(query_string),
            body=body,
        )
        rule_result = self.rule_engine.inspect(
            path=path,
            query_string=query_string,
            headers=headers,
            body=body,
        )
        findings = (
            metadata_result.get("findings", [])
            + rule_result.get("findings", [])
        )
        result = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "component": "WAF",
            "mode": self.mode,
            "status": "alert" if findings else "ok",
            "findings": findings,
            "finding_count": len(findings),
            "request_blocked": False,
            "system_firewall_modified": False,
        }
        if findings:
            # Do not log raw request bodies, query strings, or header values.
            self.event_logger.log_event({
                "status": result["status"],
                "finding_count": result["finding_count"],
                "findings": findings,
                "path": self._safe_path(path),
            })
        return result
    @staticmethod
    def _parse_query_parameters(query_string: str) -> Dict[str, str]:
        """Count query parameters without requiring a web framework."""
        from urllib.parse import parse_qsl
        if not isinstance(query_string, str):
            return {}
        try:
            pairs = parse_qsl(
                query_string,
                keep_blank_values=True,
                max_num_fields=10000,
            )
            return {key: value for key, value in pairs}
        except (ValueError, TypeError):
            return {}
    @staticmethod
    def _safe_path(path: Any) -> str:
        """Avoid storing query strings and fragments in the logged path."""
        if not isinstance(path, str):
            return "[INVALID_PATH]"
        return path.split("?", 1)[0].split("#", 1)[0]
    def health(self) -> Dict[str, Any]:
        """Return basic WAF manager status."""
        return {
            "project": "Tamanna AI",
            "component": "WAF",
            "enabled": self.enabled,
            "mode": self.mode,
            "request_blocking": False,
            "system_firewall_modification": False,
            "status": "ok",
        }