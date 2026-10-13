"""Tamanna AI WAF detection rule engine.
Detects common suspicious patterns for monitoring.
This is a basic heuristic detector, not a complete security solution.
"""
import re
from typing import Any, Dict, List, Mapping
class RuleEngine:
    """Detect common suspicious request patterns."""
    PATTERNS = {
        "sql_injection": re.compile(
            r"\bunion\s+(?:all\s+)?select\b"
            r"|\bselect\b.{0,80}\bfrom\b"
            r"|\bor\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+"
            r"|(?:--|/\*|\*/|;)",
            re.IGNORECASE,
        ),
        "cross_site_scripting": re.compile(
            r"<\s*script\b"
            r"|javascript\s*:"
            r"|\bonerror\s*="
            r"|\bonload\s*="
            r"|<\s*iframe\b",
            re.IGNORECASE,
        ),
        "path_traversal": re.compile(
            r"(?:\.\./|\.\.\\|%2e%2e(?:%2f|%5c))",
            re.IGNORECASE,
        ),
    }
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.detection = dict(self.config.get("detection", {}))
        self.rules = dict(self.config.get("rules", {}))
    @staticmethod
    def _to_text(value: Any) -> str:
        """Convert supported input values to text safely."""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, (str, int, float)):
            return str(value)
        return ""
    def inspect(
        self,
        path: str = "/",
        query_string: str = "",
        headers: Mapping[str, Any] = None,
        body: Any = "",
    ) -> Dict[str, Any]:
        """Return suspicious-pattern findings without blocking requests."""
        headers = headers or {}
        findings: List[Dict[str, str]] = []
        targets: List[tuple] = []
        if self.rules.get("inspect_path", True):
            targets.append(("path", self._to_text(path)))
        if self.rules.get("inspect_query_string", True):
            targets.append(("query", self._to_text(query_string)))
        if self.rules.get("inspect_headers", True):
            for name, value in headers.items():
                targets.append((
                    "header",
                    self._to_text(name) + ": " + self._to_text(value),
                ))
        if self.rules.get("inspect_request_body", True):
            maximum = int(
                self.rules.get("maximum_body_inspection_bytes", 65536)
            )
            if isinstance(body, bytes):
                body_text = body[:maximum].decode(
                    "utf-8", errors="replace"
                )
            else:
                body_text = self._to_text(body)[:maximum]
            targets.append(("body", body_text))
        for source, text in targets:
            for rule_name, pattern in self.PATTERNS.items():
                if (
                    rule_name == "sql_injection"
                    and not self.detection.get(
                        "sql_injection_detection", True
                    )
                ):
                    continue
                if (
                    rule_name == "cross_site_scripting"
                    and not self.detection.get(
                        "cross_site_scripting_detection", True
                    )
                ):
                    continue
                if (
                    rule_name == "path_traversal"
                    and not self.detection.get(
                        "path_traversal_detection", True
                    )
                ):
                    continue
                if pattern.search(text):
                    findings.append({
                        "rule": rule_name,
                        "source": source,
                        "severity": "high",
                        "reason": (
                            "A suspicious pattern matched a WAF detection rule."
                        ),
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