"""Tests for Streamlit-independent application orchestration."""

from pathlib import Path

from electricvehicles.application import build_page_context, load_application_data
from electricvehicles.filtering import FilterSelection

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def test_application_load_builds_full_snapshot_artifacts() -> None:
    application = load_application_data(FIXTURE)

    assert len(application.clean_data) == 2
    assert application.validation_report.is_valid
    assert application.quality_report.row_count == 2
    assert application.source_path == FIXTURE.resolve()


def test_page_context_keeps_full_quality_and_filtered_rows() -> None:
    application = load_application_data(FIXTURE)
    selection = FilterSelection(
        washington_only=True,
        model_year_min=2020,
        model_year_max=2020,
    )

    context = build_page_context(application, selection)

    assert len(context.filtered_data) == 1
    assert context.application.quality_report.row_count == 2
