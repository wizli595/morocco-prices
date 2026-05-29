"""Tests for outlier flagger."""

from src.core.transformers.outlier_flagger import flag_outliers


def test_no_outliers_in_normal_data():
    values = [("a", 10.0), ("b", 11.0), ("c", 10.5), ("d", 10.8)]
    results = flag_outliers(values)
    assert all(not r.is_outlier for r in results)


def test_detects_extreme_outlier():
    values = [
        ("a", 10.0), ("b", 10.1), ("c", 10.2),
        ("d", 10.0), ("e", 10.1), ("f", 500.0),
    ]
    results = flag_outliers(values, threshold=2.0)
    outliers = [r for r in results if r.is_outlier]
    assert len(outliers) == 1
    assert outliers[0].observation_id == "f"


def test_too_few_values_no_flag():
    values = [("a", 10.0), ("b", 500.0)]
    results = flag_outliers(values)
    assert all(not r.is_outlier for r in results)


def test_all_same_no_flag():
    values = [("a", 10.0), ("b", 10.0), ("c", 10.0)]
    results = flag_outliers(values)
    assert all(not r.is_outlier for r in results)


def test_zscore_populated():
    values = [("a", 10.0), ("b", 11.0), ("c", 10.5), ("d", 10.8)]
    results = flag_outliers(values)
    assert all(isinstance(r.zscore, float) for r in results)
