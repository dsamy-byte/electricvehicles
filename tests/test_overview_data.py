"""Tests for Overview metric definitions and denominator behavior."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.overview_data import build_overview_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Return the two-row cleaned vehicle fixture."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def test_overview_metrics_use_full_filtered_denominator(
    clean_fixture: pd.DataFrame,
) -> None:
    overview = build_overview_data(clean_fixture)

    assert overview.vehicle_count == 2
    assert overview.bev_count == 1
    assert overview.bev_share == 0.5
    assert overview.median_model_year == 2021.5
    assert overview.known_range_count == 1
    assert overview.known_range_share == 0.5
    assert overview.eligible_count == 1
    assert overview.eligible_share == 0.5


def test_overview_series_are_ordered_for_their_visuals(
    clean_fixture: pd.DataFrame,
) -> None:
    overview = build_overview_data(clean_fixture)

    assert [item.value for item in overview.model_years] == ["2020", "2023"]
    assert [item.value for item in overview.top_makes] == ["JEEP", "TESLA"]


def test_unknown_values_remain_in_metric_denominators(
    clean_fixture: pd.DataFrame,
) -> None:
    clean_fixture.loc[0, "cafv_status"] = "Unknown"
    clean_fixture.loc[0, "electric_range_miles"] = pd.NA

    overview = build_overview_data(clean_fixture)

    assert overview.known_range_share == 0.0
    assert overview.eligible_share == 0.0
    assert overview.vehicle_count == 2


def test_overview_requires_non_empty_clean_data(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="at least one filtered vehicle"):
        build_overview_data(clean_fixture.iloc[0:0])


def test_overview_rejects_invalid_make_limit(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="make limit"):
        build_overview_data(clean_fixture, top_make_limit=0)
