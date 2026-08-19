"""Tests for market identity, ranking, concentration, and heatmap behavior."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.market_data import build_market_data

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Return the two-row cleaned vehicle fixture."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def test_market_metrics_and_rankings(clean_fixture: pd.DataFrame) -> None:
    market = build_market_data(clean_fixture)

    assert market.vehicle_count == 2
    assert market.make_count == 2
    assert market.make_model_count == 2
    assert market.leading_make == "JEEP"
    assert market.leading_make_share == 0.5
    assert market.top_10_make_share == 1.0
    assert [rank.make for rank in market.make_rankings] == ["JEEP", "TESLA"]


def test_model_identity_includes_make(clean_fixture: pd.DataFrame) -> None:
    duplicate_label = clean_fixture.iloc[[0]].copy()
    duplicate_label.loc[:, "dol_vehicle_id"] = "300000001"
    duplicate_label.loc[:, "make"] = "ANOTHER MAKE"
    combined = pd.concat([clean_fixture, duplicate_label], ignore_index=True)

    market = build_market_data(combined)
    matching = [rank for rank in market.model_rankings if rank.model == "MODEL 3"]

    assert len(matching) == 2
    assert {rank.make for rank in matching} == {"TESLA", "ANOTHER MAKE"}


def test_cumulative_share_is_monotonic_and_complete(
    clean_fixture: pd.DataFrame,
) -> None:
    market = build_market_data(clean_fixture)
    shares = [rank.cumulative_share for rank in market.make_rankings]

    assert shares == sorted(shares)
    assert shares[-1] == 1.0


def test_heatmap_grid_includes_zero_cells(clean_fixture: pd.DataFrame) -> None:
    market = build_market_data(clean_fixture)
    lookup = {(cell.make, cell.model_year): cell.count for cell in market.heatmap_cells}

    assert lookup[("JEEP", 2020)] == 0
    assert lookup[("JEEP", 2023)] == 1
    assert lookup[("TESLA", 2020)] == 1
    assert len(market.heatmap_cells) == 4


def test_market_data_does_not_mutate_source(clean_fixture: pd.DataFrame) -> None:
    original = clean_fixture.copy(deep=True)

    build_market_data(clean_fixture)

    pd.testing.assert_frame_equal(clean_fixture, original)


def test_market_data_requires_clean_columns(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Market analysis requires clean columns"):
        build_market_data(clean_fixture.drop(columns="model"))


def test_heatmap_limit_must_be_positive(clean_fixture: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Heatmap make limit"):
        build_market_data(clean_fixture, heatmap_make_limit=0)
