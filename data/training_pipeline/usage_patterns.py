"""Corpus-relative heuristic analysis of common code patterns."""
from __future__ import annotations
import re
from collections import Counter
from typing import Iterable, Mapping

_PATTERNS = {
    "function_definition": re.compile(r"\b(?:def\s+\w+\s*\(|function\s+\w+\s*\(|fn\s+\w+\s*\(|func\s+\w+\s*\()"),
    "class_definition": re.compile(r"\b(?:class\s+\w+|struct\s+\w+|interface\s+\w+)"),
    "async_concurrency": re.compile(r"\b(?:async\s+def|async\s+function|await\s+|Promise\.all|goroutine)"),
    "exception_handling": re.compile(r"\b(?:try\s*:|try\s*\{|catch\s*\(|except\b|finally\s*:)"),
    "automated_testing": re.compile(r"\b(?:pytest|unittest|describe\s*\(|it\s*\(|test\w*\s*\(|assert\w*\s*\()"),
    "http_api": re.compile(r"\b(?:fetch\s*\(|axios\.|requests\.(?:get|post|put|delete)|httpx\.|FastAPI\s*\()"),
    "database_sql": re.compile(r"\b(?:SELECT\s+.+\s+FROM|INSERT\s+INTO|CREATE\s+TABLE|sqlite3\.|\.execute\s*\()"),
    "file_io": re.compile(r"\b(?:open\s*\(|readFile(?:Sync)?\s*\(|writeFile(?:Sync)?\s*\(|Path\s*\()"),
    "serialization": re.compile(r"\b(?:json\.(?:loads|dumps|load|dump)|JSON\.(?:parse|stringify)|serde_json)"),
    "logging_observability": re.compile(r"\b(?:logging\.|logger\.|console\.(?:log|error|warn))"),
    "iteration": re.compile(r"\b(?:for\s+\w+\s+in\b|for\s*\(|while\s*\(|\.map\s*\(|\.forEach\s*\()"),
}

def analyze_code_patterns(records: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Count at most once per pattern per source sample."""
    counts: Counter[str] = Counter()
    evidence: dict[str, list[str]] = {name: [] for name in _PATTERNS}
    samples = 0
    for record in records:
        source = record.get("text", "")
        if not isinstance(source, str) or not source.strip():
            continue
        samples += 1
        path = str(record.get("path") or record.get("source") or f"sample-{samples}")[:300]
        for name, pattern in _PATTERNS.items():
            if pattern.search(source):
                counts[name] += 1
                if len(evidence[name]) < 10 and path not in evidence[name]:
                    evidence[name].append(path)
    return {
        "sample_count": samples,
        "measurement": "share of supplied code samples containing each heuristic pattern",
        "not_industry_usage_statistics": True,
        "patterns": [
            {"pattern": name, "sample_count": count,
             "corpus_share": round(count / samples, 4) if samples else 0.0,
             "evidence_sources": evidence[name]}
            for name, count in counts.most_common()
        ],
    }

__all__ = ["analyze_code_patterns"]
