"""Tests for shared, presentation-independent dashboard filter semantics."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import load_clean_data
from electricvehicles.filtering import (
    FilterSelection,
    apply_filters,
    available_values,
    describe_filters,
)

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    """Return the two-row cleaned fixture used by filter tests."""
    cleaned, _ = load_clean_data(FIXTURE)
    return cleaned


def full_selection(**overrides) -> FilterSelection:
    """Build the fixture's default all-values filter with optional changes."""
    values = {
        "washington_only": True,
        "model_year_min": 2020,
        "model_year_max": 2023,
    }
    values.update(overrides)
    return FilterSelection(**values)


def test_empty_categories_mean_all_values(clean_fixture: pd.DataFrame) -> None:
    result = apply_filters(clean_fixture, full_selection())

    assert len(result) == 2


def test_filters_compose_across_fields(clean_fixture: pd.DataFrame) -> None:
    result = apply_filters(
        clean_fixture,
        full_selection(ev_types=("BEV",), makes=("TESLA",), counties=("Yakima",)),
    )

    assert result["dol_vehicle_id"].tolist() == ["102765120"]


def test_model_year_bounds_are_inclusive(clean_fixture: pd.DataFrame) -> None:
    result = apply_filters(
        clean_fixture,
        full_selection(model_year_min=2023, model_year_max=2023),
    )

    assert result["model_year"].tolist() == [2023]


def test_washington_scope_can_be_disabled(clean_fixture: pd.DataFrame) -> None:
    clean_fixture.loc[0, "state"] = "OR"

    wa_only = apply_filters(clean_fixture, full_selection())
    all_states = apply_filters(clean_fixture, full_selection(washington_only=False))

    assert len(wa_only) == 1
    assert len(all_states) == 2


def test_filtering_returns_copy(clean_fixture: pd.DataFrame) -> None:
    result = apply_filters(clean_fixture, full_selection())
    result.loc[result.index[0], "make"] = "CHANGED"

    assert clean_fixture.loc[clean_fixture.index[0], "make"] == "TESLA"


def test_inverted_year_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="Minimum model year"):
        full_selection(model_year_min=2024, model_year_max=2023)


def test_options_are_deterministic_and_ignore_missing(
    clean_fixture: pd.DataFrame,
) -> None:
    clean_fixture.loc[0, "county"] = pd.NA

    assert available_values(clean_fixture, "county") == ("King",)


def test_filter_description_discloses_scope_and_selections() -> None:
    description = describe_filters(
        full_selection(ev_types=("BEV",), makes=("TESLA", "FORD", "KIA"))
    )

    assert "Washington only" in description
    assert "BEV" in description
    assert "3 makes selected" in description
