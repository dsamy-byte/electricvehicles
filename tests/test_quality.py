"""Tests for quality measurement, drift detection, and JSON export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.quality import (
    QualityBaselineError,
    build_quality_report,
    load_quality_baseline,
    write_quality_report,
)

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture():
    """Return clean fixture data and the validation report used to produce it."""
    return load_clean_data(FIXTURE)


@pytest.fixture
def fixture_baseline() -> dict:
    """Return permissive thresholds sized for the two-row test fixture."""
    return {
        "version": 1,
        "row_count": {"expected": 2, "relative_tolerance": 0.0},
        "maximum_missing_rates": {
            "county": 0.0,
            "city": 0.0,
            "postal_code": 0.0,
            "electric_range_raw": 0.0,
            "legislative_district": 0.0,
            "vehicle_location": 0.0,
            "electric_utility": 0.0,
            "census_tract_2020": 0.0,
        },
        "maximum_exact_duplicate_rows": 0,
        "maximum_duplicate_vehicle_ids": 0,
        "unknown_range_rate": {"expected": 0.5, "absolute_tolerance": 0.0},
        "washington_share": {"expected": 1.0, "absolute_tolerance": 0.0},
    }


def test_quality_report_measures_fixture(clean_fixture, fixture_baseline) -> None:
    cleaned, validation = clean_fixture

    report = build_quality_report(cleaned, validation, baseline=fixture_baseline)

    assert report.row_count == 2
    assert report.column_count == 22
    assert report.exact_duplicate_rows == 0
    assert report.duplicate_vehicle_ids == 0
    assert report.unknown_range_count == 1
    assert report.unknown_range_rate == 0.5
    assert report.complete_coordinate_rate == 1.0
    assert report.washington_share == 1.0
    assert report.columns["make"].unique_count == 2
    assert report.is_within_baseline


def test_baseline_failure_is_visible_without_hiding_metrics(
    clean_fixture, fixture_baseline
) -> None:
    cleaned, validation = clean_fixture
    fixture_baseline["row_count"]["expected"] = 3

    report = build_quality_report(cleaned, validation, baseline=fixture_baseline)

    assert not report.is_within_baseline
    failed = [check for check in report.baseline_checks if not check.passed]
    assert [check.metric for check in failed] == ["row_count"]
    assert report.row_count == 2


def test_missing_rate_regression_fails_named_check(
    clean_fixture, fixture_baseline
) -> None:
    cleaned, validation = clean_fixture
    cleaned.loc[0, "county"] = None

    report = build_quality_report(cleaned, validation, baseline=fixture_baseline)

    failures = {check.metric for check in report.baseline_checks if not check.passed}
    assert "missing_rate.county" in failures
    assert report.columns["county"].missing_rate == 0.5


def test_validation_warnings_are_preserved(clean_fixture, fixture_baseline) -> None:
    cleaned, validation = clean_fixture
    validation.warn("example_warning", "Example warning for testing.", 1)

    report = build_quality_report(cleaned, validation, baseline=fixture_baseline)

    assert report.validation_warnings == (
        "[example_warning] Example warning for testing. (1 rows)",
    )


def test_report_requires_clean_schema(clean_fixture, fixture_baseline) -> None:
    cleaned, validation = clean_fixture

    with pytest.raises(ValueError, match="electric_range_miles"):
        build_quality_report(
            cleaned.drop(columns="electric_range_miles"),
            validation,
            baseline=fixture_baseline,
        )


def test_report_serialization_and_write(
    clean_fixture, fixture_baseline, tmp_path: Path
) -> None:
    cleaned, validation = clean_fixture
    report = build_quality_report(cleaned, validation, baseline=fixture_baseline)

    output = write_quality_report(report, tmp_path / "quality.json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["is_within_baseline"] is True
    assert payload["columns"]["postal_code"]["missing_count"] == 0


def test_project_baseline_is_versioned_and_loadable() -> None:
    baseline = load_quality_baseline()

    assert baseline["version"] == 1
    assert baseline["row_count"]["expected"] == 294193


def test_invalid_baseline_has_actionable_error(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text('{"version": 99}', encoding="utf-8")

    with pytest.raises(QualityBaselineError, match="version 1"):
        load_quality_baseline(path)
