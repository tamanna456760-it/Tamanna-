"""Regression tests for safe, low-noise analyzer secret detection."""

from scripts.analyzer import analyze_python


def _scan(tmp_path, source):
    path = tmp_path / "sample.py"
    path.write_text(source, encoding="utf-8")
    findings = []
    analyze_python(path, findings)
    return findings


def test_secret_scanner_ignores_commented_api_examples(tmp_path):
    findings = _scan(
        tmp_path,
        '# client = APIClient(api_key="your_weather_key")\n'
        '"""Example: api_key="documented-example-value" """\n',
    )
    assert not [item for item in findings if item["category"] == "POSSIBLE_SECRET"]


def test_secret_scanner_ignores_known_fake_test_key(tmp_path):
    findings = _scan(
        tmp_path,
        'client = GeminiClient(api_key="ignored-test-key")\n',
    )
    assert not [item for item in findings if item["category"] == "POSSIBLE_SECRET"]


def test_secret_scanner_still_flags_non_placeholder_values(tmp_path):
    findings = _scan(
        tmp_path,
        'API_KEY = "possibly-real-secret-value-123"\n',
    )
    assert [item for item in findings if item["category"] == "POSSIBLE_SECRET"]
