"""Tests for geographic identity, coverage, ranking, and privacy aggregation."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.geography_data import build_geography_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Return the two-row cleaned vehicle fixture."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def test_geography_metrics_and_rankings(clean_fixture: pd.DataFrame) -> None:
    geography = build_geography_data(clean_fixture)

    assert geography.vehicle_count == 2
    assert geography.state_count == 1
    assert geography.county_count == 2
    assert geography.city_count == 2
    assert geography.leading_county == "King, WA"
    assert geography.leading_county_share == 0.5
    assert [item.label for item in geography.city_rankings] == [
        "Seattle, WA",
        "Yakima, WA",
    ]


def test_same_named_counties_in_different_states_remain_distinct(
    clean_fixture: pd.DataFrame,
) -> None:
    extra = clean_fixture.iloc[[0]].copy()
    extra.loc[:, "dol_vehicle_id"] = "300000001"
    extra.loc[:, "state"] = "OR"
    combined = pd.concat([clean_fixture, extra], ignore_index=True)

    geography = build_geography_data(combined)
    yakima = [item for item in geography.county_rankings if item.county == "Yakima"]

    assert len(yakima) == 2
    assert {item.state for item in yakima} == {"WA", "OR"}


def test_map_points_are_aggregated_and_exclude_identifiers(
    clean_fixture: pd.DataFrame,
) -> None:
    duplicate = clean_fixture.iloc[[0]].copy()
    duplicate.loc[:, "dol_vehicle_id"] = "300000001"
    combined = pd.concat([clean_fixture, duplicate], ignore_index=True)

    geography = build_geography_data(combined)
    yakima = [point for point in geography.map_points if point.city == "Yakima"]

    assert len(yakima) == 1
    assert yakima[0].count == 2
    assert "dol_vehicle_id" not in yakima[0].__dataclass_fields__


def test_coordinate_coverage_keeps_missing_values_visible(
    clean_fixture: pd.DataFrame,
) -> None:
    clean_fixture.loc[0, ["longitude", "latitude"]] = pd.NA

    geography = build_geography_data(clean_fixture)

    assert geography.coordinate_vehicle_count == 1
    assert geography.coordinate_coverage == 0.5


def test_geography_data_does_not_mutate_source(clean_fixture: pd.DataFrame) -> None:
    original = clean_fixture.copy(deep=True)

    build_geography_data(clean_fixture)

    pd.testing.assert_frame_equal(clean_fixture, original)


def test_geography_requires_clean_columns(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Geography analysis requires clean columns"):
        build_geography_data(clean_fixture.drop(columns="latitude"))
