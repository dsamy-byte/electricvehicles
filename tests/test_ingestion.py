"""Tests for raw CSV ingestion and contract validation."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pytest

from electricvehicles.data_contract import SOURCE_COLUMNS
from electricvehicles.ingestion import DataLoadError, load_raw_data, load_validated_data
from electricvehicles.validation import DataValidationError, validate_dataframe

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def test_load_valid_fixture_preserves_strings() -> None:
    frame, report = load_validated_data(FIXTURE)

    assert frame.shape == (2, 16)
    assert tuple(frame.columns) == SOURCE_COLUMNS
    assert all(dtype.name == "string" for dtype in frame.dtypes)
    assert frame.loc[1, "Electric Range"] == "0"
    assert report.is_valid
    assert not report.warnings


def test_missing_file_has_actionable_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(DataLoadError, match="EV_DATA_PATH"):
        load_raw_data(missing)


def test_missing_column_is_rejected(tmp_path: Path) -> None:
    frame = pd.read_csv(FIXTURE, dtype="string")
    path = tmp_path / "missing-column.csv"
    frame.drop(columns="County").to_csv(path, index=False)

    with pytest.raises(DataLoadError, match=r"Missing: \['County'\]"):
        load_raw_data(path)


def test_duplicate_header_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-header.csv"
    rows = list(csv.reader(FIXTURE.open(encoding="utf-8", newline="")))
    rows[0][-1] = "VIN (1-10)"
    with path.open("w", encoding="utf-8", newline="") as target:
        csv.writer(target).writerows(rows)

    with pytest.raises(DataLoadError, match="duplicate column names"):
        load_raw_data(path)


def test_duplicate_vehicle_id_is_blocking() -> None:
    frame = load_raw_data(FIXTURE)
    frame.loc[1, "DOL Vehicle ID"] = frame.loc[0, "DOL Vehicle ID"]

    report = validate_dataframe(frame)

    assert not report.is_valid
    assert "duplicate_vehicle_id" in {issue.code for issue in report.errors}


def test_unreviewed_vehicle_type_is_blocking() -> None:
    frame = load_raw_data(FIXTURE)
    frame.loc[0, "Electric Vehicle Type"] = "Hydrogen"

    report = validate_dataframe(frame)

    assert not report.is_valid
    assert "unexpected_category" in {issue.code for issue in report.errors}


def test_invalid_optional_geography_produces_warnings() -> None:
    frame = load_raw_data(FIXTURE)
    frame.loc[0, "Postal Code"] = "ABC"
    frame.loc[0, "2020 Census Tract"] = "123"
    frame.loc[0, "Vehicle Location"] = "POINT (500 200)"
    frame.loc[0, "Legislative District"] = "50"

    report = validate_dataframe(frame)
    warning_codes = {issue.code for issue in report.warnings}

    assert report.is_valid
    assert {
        "invalid_postal_format",
        "invalid_census_tract",
        "invalid_vehicle_location",
        "invalid_legislative_district",
    } <= warning_codes


def test_validation_exception_exposes_report(tmp_path: Path) -> None:
    frame = pd.read_csv(FIXTURE, dtype="string", keep_default_na=False)
    frame.loc[0, "Electric Range"] = "-1"
    path = tmp_path / "negative-range.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(DataValidationError) as caught:
        load_validated_data(path)

    assert "negative_electric_range" in {
        issue.code for issue in caught.value.report.errors
    }
