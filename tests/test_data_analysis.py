import csv

import pytest

from tamanna_ai.knowledge.analytics import analyze_file


def test_csv_analysis_returns_numeric_summary_and_chart_data(tmp_path):
    path = tmp_path / "sales.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["month", "revenue", "cost"])
        writer.writerow(["Jan", "100", "60"])
        writer.writerow(["Feb", "150", "90"])
    result = analyze_file(path)
    assert result["row_count"] == 2
    assert result["columns"]["revenue"]["sum"] == 250
    assert result["columns"]["cost"]["mean"] == 75
    assert result["chart_data"]["series"] == ["revenue", "cost"]


def test_rejects_unsupported_and_symlink_files(tmp_path):
    bad = tmp_path / "data.exe"
    bad.write_text("no", encoding="utf-8")
    with pytest.raises(ValueError):
        analyze_file(bad)
    target = tmp_path / "target.csv"
    target.write_text("a\n1\n", encoding="utf-8")
    link = tmp_path / "link.csv"
    link.symlink_to(target)
    with pytest.raises(ValueError):
        analyze_file(link)


def test_rejects_empty_csv(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        analyze_file(path)
