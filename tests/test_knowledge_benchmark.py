from __future__ import annotations

from scripts.benchmark_knowledge_search import benchmark_size


def test_small_knowledge_scale_benchmark_reports_latency_metrics():
    result = benchmark_size(100, repeats=2)

    assert result["records"] == 100
    assert result["search_repeats"] == 2
    assert result["returned_results"] == 1
    assert result["seed_seconds"] >= 0
    assert result["median_search_ms"] >= 0
    assert result["p95_search_ms"] >= 0
    assert result["max_search_ms"] >= result["median_search_ms"]
