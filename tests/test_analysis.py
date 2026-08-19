"""Tests for presentation-neutral exploratory analysis."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.analysis import (
    build_exploratory_analysis,
    category_breakdown,
)
from electricvehicles.cleaning import load_clean_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Load the two-row analysis-ready fixture."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def test_category_breakdown_uses_all_rows_as_denominator(
    clean_fixture: pd.DataFrame,
) -> None:
    clean_fixture.loc[1, "county"] = pd.NA

    results = category_breakdown(clean_fixture, "county")

    assert len(results) == 1
    assert results[0].count == 1
    assert results[0].share == 0.5


def test_rank_ties_are_deterministic(clean_fixture: pd.DataFrame) -> None:
    results = category_breakdown(clean_fixture, "make")

    assert [result.value for result in results] == ["JEEP", "TESLA"]


def test_invalid_category_limit_is_rejected(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="positive"):
        category_breakdown(clean_fixture, "make", limit=0)


def test_exploratory_summary_counts_and_concentration(
    clean_fixture: pd.DataFrame,
) -> None:
    analysis = build_exploratory_analysis(clean_fixture)

    assert analysis.vehicle_count == 2
    assert analysis.model_year_min == 2020
    assert analysis.model_year_max == 2023
    assert analysis.model_year_median == 2021.5
    assert analysis.make_count == 2
    assert analysis.top_10_make_share == 1.0
    assert analysis.top_5_county_share == 1.0
    assert analysis.recent_model_year_count == 1
    assert analysis.recent_model_year_share == 0.5


def test_range_analysis_excludes_unknown_zero_range(
    clean_fixture: pd.DataFrame,
) -> None:
    analysis = build_exploratory_analysis(clean_fixture)
    ranges = {item.ev_type_code: item for item in analysis.range_by_vehicle_type}

    assert ranges["BEV"].known_range_count == 1
    assert ranges["BEV"].median_miles == 266
    assert ranges["PHEV"].known_range_count == 0
    assert ranges["PHEV"].median_miles is None


def test_model_year_output_is_chronological(clean_fixture: pd.DataFrame) -> None:
    years = build_exploratory_analysis(clean_fixture).model_years

    assert [item.value for item in years] == ["2020", "2023"]


def test_analysis_does_not_mutate_clean_data(clean_fixture: pd.DataFrame) -> None:
    original = clean_fixture.copy(deep=True)

    build_exploratory_analysis(clean_fixture)

    pd.testing.assert_frame_equal(clean_fixture, original)


def test_analysis_requires_clean_schema(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="electric_range_miles"):
        build_exploratory_analysis(clean_fixture.drop(columns="electric_range_miles"))


def test_analysis_serializes_to_json(clean_fixture: pd.DataFrame) -> None:
    payload = build_exploratory_analysis(clean_fixture).to_json()

    assert '"vehicle_count": 2' in payload
    assert '"ev_type_code": "BEV"' in payload
