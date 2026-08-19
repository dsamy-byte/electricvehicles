"""Tests for coverage-aware range and CAFV calculations."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.range_cafv_data import build_range_cafv_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Return the two-row cleaned vehicle fixture."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def test_headline_metrics_keep_unknowns_in_denominator(
    clean_fixture: pd.DataFrame,
) -> None:
    data = build_range_cafv_data(clean_fixture)

    assert data.vehicle_count == 2
    assert data.known_range_count == 1
    assert data.known_range_share == 0.5
    assert data.median_known_range == 266
    assert data.eligible_share == 0.5
    assert data.unknown_cafv_share == 0.5


def test_coverage_remains_separate_by_vehicle_type(
    clean_fixture: pd.DataFrame,
) -> None:
    data = build_range_cafv_data(clean_fixture)
    coverage = {item.ev_type_code: item for item in data.coverage_by_type}

    assert coverage["BEV"].known_count == 1
    assert coverage["BEV"].known_share == 1.0
    assert coverage["PHEV"].known_count == 0
    assert coverage["PHEV"].unknown_count == 1


def test_statistics_do_not_treat_unknown_range_as_zero(
    clean_fixture: pd.DataFrame,
) -> None:
    data = build_range_cafv_data(clean_fixture)
    statistics = {item.ev_type_code: item for item in data.statistics_by_type}

    assert statistics["BEV"].minimum_miles == 266
    assert statistics["BEV"].median_miles == 266
    assert statistics["PHEV"].minimum_miles is None
    assert statistics["PHEV"].median_miles is None


def test_histogram_bins_are_fixed_width_and_aggregated(
    clean_fixture: pd.DataFrame,
) -> None:
    duplicate = clean_fixture.iloc[[0]].copy()
    duplicate.loc[:, "dol_vehicle_id"] = "300000001"
    combined = pd.concat([clean_fixture, duplicate], ignore_index=True)

    data = build_range_cafv_data(combined, bin_width_miles=10)

    assert len(data.range_bins) == 1
    assert data.range_bins[0].label == "260-269"
    assert data.range_bins[0].count == 2


def test_all_cafv_categories_remain_explicit(clean_fixture: pd.DataFrame) -> None:
    data = build_range_cafv_data(clean_fixture)

    assert {item.value for item in data.cafv_statuses} == {"Eligible", "Unknown"}


def test_range_data_does_not_mutate_source(clean_fixture: pd.DataFrame) -> None:
    original = clean_fixture.copy(deep=True)

    build_range_cafv_data(clean_fixture)

    pd.testing.assert_frame_equal(clean_fixture, original)


def test_range_bin_width_must_be_positive(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        build_range_cafv_data(clean_fixture, bin_width_miles=0)


def test_range_data_requires_clean_columns(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="requires clean columns"):
        build_range_cafv_data(clean_fixture.drop(columns="cafv_status"))
