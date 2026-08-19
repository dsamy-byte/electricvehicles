"""Tests for unfiltered provenance and methodology page view models."""

from pathlib import Path

from electricvehicles.application import load_application_data
from electricvehicles.quality_page_data import build_quality_page_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def test_quality_page_uses_full_application_snapshot() -> None:
    """Fingerprint and dimensions must describe the loaded full source."""
    application = load_application_data(FIXTURE)

    page = build_quality_page_data(application)

    assert page.row_count == 2
    assert page.column_count == 22
    assert page.source_file_name == FIXTURE.name
    assert page.source_size_bytes == FIXTURE.stat().st_size
    assert len(page.source_sha256) == 64
    assert page.warning_count == 0


def test_quality_page_contains_all_baseline_results() -> None:
    """Fixture drift remains visible instead of suppressing quality metrics."""
    page = build_quality_page_data(load_application_data(FIXTURE))

    assert page.baseline_check_count == 13
    assert len(page.baseline_results) == 13
    assert page.baseline_passed_count < page.baseline_check_count
    assert not page.baseline_passed


def test_missingness_covers_and_orders_every_clean_field() -> None:
    """Completeness output includes all fields in descending missing-rate order."""
    page = build_quality_page_data(load_application_data(FIXTURE))

    assert len(page.missingness) == 22
    rates = [item.missing_rate for item in page.missingness]
    assert rates == sorted(rates, reverse=True)
    assert {item.column for item in page.missingness} >= {
        "electric_range_raw",
        "electric_range_miles",
        "dol_vehicle_id",
    }


def test_dictionary_and_methodology_are_complete() -> None:
    """Executable page documentation covers every clean field and policy set."""
    page = build_quality_page_data(load_application_data(FIXTURE))

    assert len(page.field_definitions) == 22
    assert len(page.cleaning_rules) >= 7
    assert len(page.analytical_guardrails) >= 7
    assert any(
        definition.clean_name == "electric_range_miles"
        for definition in page.field_definitions
    )
