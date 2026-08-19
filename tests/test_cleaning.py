"""Tests for deterministic, audit-friendly data preparation."""

from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.cleaning import clean_data, load_clean_data
from electricvehicles.ingestion import load_raw_data
from electricvehicles.validation import DataValidationError

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


@pytest.fixture
def raw_data() -> pd.DataFrame:
    """Return a fresh validated-shape source fixture for each test."""
    return load_raw_data(FIXTURE)


def test_cleaning_does_not_mutate_source(raw_data: pd.DataFrame) -> None:
    original = raw_data.copy(deep=True)

    clean_data(raw_data)

    pd.testing.assert_frame_equal(raw_data, original)


def test_columns_are_renamed_and_features_are_added(raw_data: pd.DataFrame) -> None:
    cleaned = clean_data(raw_data)

    assert "VIN (1-10)" not in cleaned.columns
    assert {
        "vin_prefix",
        "electric_range_raw",
        "electric_range_miles",
        "ev_type_code",
        "cafv_status",
        "is_washington",
        "longitude",
        "latitude",
    } <= set(cleaned.columns)


def test_zero_range_becomes_missing_only_in_analysis_field(
    raw_data: pd.DataFrame,
) -> None:
    cleaned = clean_data(raw_data)

    assert cleaned.loc[1, "electric_range_raw"] == 0
    assert pd.isna(cleaned.loc[1, "electric_range_miles"])
    assert cleaned.loc[0, "electric_range_miles"] == 266
    assert cleaned["electric_range_miles"].dtype == "Int64"


def test_identifier_types_and_leading_zero_are_preserved(
    raw_data: pd.DataFrame,
) -> None:
    raw_data.loc[0, "Postal Code"] = "1234"

    cleaned = clean_data(raw_data)

    assert cleaned.loc[0, "postal_code"] == "01234"
    assert cleaned["postal_code"].dtype.name == "string"
    assert cleaned["dol_vehicle_id"].dtype.name == "string"
    assert cleaned["census_tract_2020"].dtype.name == "string"


def test_text_and_display_categories_are_normalized(raw_data: pd.DataFrame) -> None:
    raw_data.loc[0, "Make"] = "  tesla  "
    raw_data.loc[0, "County"] = "King   County"

    cleaned = clean_data(raw_data)

    assert cleaned.loc[0, "make"] == "TESLA"
    assert cleaned.loc[0, "county"] == "King County"
    assert cleaned["ev_type_code"].tolist() == ["BEV", "PHEV"]
    assert cleaned["cafv_status"].tolist() == ["Eligible", "Unknown"]


def test_location_is_parsed_and_source_wkt_is_retained(raw_data: pd.DataFrame) -> None:
    cleaned = clean_data(raw_data)

    assert cleaned.loc[0, "vehicle_location"] == "POINT (-120.60272 46.59656)"
    assert cleaned.loc[0, "longitude"] == pytest.approx(-120.60272)
    assert cleaned.loc[0, "latitude"] == pytest.approx(46.59656)
    assert cleaned["longitude"].dtype == "Float64"


def test_nullable_values_remain_nullable(raw_data: pd.DataFrame) -> None:
    raw_data.loc[0, "Electric Range"] = pd.NA
    raw_data.loc[0, "Vehicle Location"] = pd.NA

    cleaned = clean_data(raw_data)

    assert pd.isna(cleaned.loc[0, "electric_range_raw"])
    assert pd.isna(cleaned.loc[0, "electric_range_miles"])
    assert pd.isna(cleaned.loc[0, "longitude"])
    assert pd.isna(cleaned.loc[0, "latitude"])


def test_cleaning_rejects_unvalidated_source(raw_data: pd.DataFrame) -> None:
    raw_data.loc[0, "DOL Vehicle ID"] = "-5"

    with pytest.raises(DataValidationError, match="non_positive_vehicle_id"):
        clean_data(raw_data)


def test_end_to_end_clean_loader_returns_warnings_and_clean_data() -> None:
    cleaned, report = load_clean_data(FIXTURE)

    assert report.is_valid
    assert not report.warnings
    assert cleaned.shape == (2, 22)
    assert cleaned["model_year"].dtype == "Int64"
    assert cleaned["is_washington"].all()
