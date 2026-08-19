"""Raw-data ingestion for the Electric Vehicles dashboard."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from electricvehicles.config import get_data_path
from electricvehicles.data_contract import SOURCE_COLUMNS
from electricvehicles.validation import (
    DataValidationError,
    ValidationReport,
    validate_dataframe,
)


class DataLoadError(RuntimeError):
    """Raised when a source file cannot be safely loaded."""


def _validate_header(path: Path) -> None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as source:
            header = next(csv.reader(source), None)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DataLoadError(f"Could not read CSV header from {path}: {exc}") from exc

    if header is None:
        raise DataLoadError(f"Source file is empty: {path}")
    duplicates = sorted({name for name in header if header.count(name) > 1})
    if duplicates:
        raise DataLoadError(
            f"Source CSV contains duplicate column names: {', '.join(duplicates)}"
        )
    if tuple(header) != SOURCE_COLUMNS:
        missing = [name for name in SOURCE_COLUMNS if name not in header]
        unexpected = [name for name in header if name not in SOURCE_COLUMNS]
        raise DataLoadError(
            "Source CSV columns do not match the contract. "
            f"Missing: {missing or 'none'}; unexpected: {unexpected or 'none'}; "
            "column order must match the published schema."
        )


def load_raw_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the raw CSV as nullable strings without cleaning source values."""
    source_path = get_data_path(path)
    if not source_path.is_file():
        raise DataLoadError(
            f"Electric vehicle source file was not found at {source_path}. "
            "Set EV_DATA_PATH or place the file at data/raw/electric.csv."
        )

    _validate_header(source_path)
    try:
        return pd.read_csv(
            source_path,
            dtype="string",
            encoding="utf-8-sig",
            keep_default_na=False,
            na_values=[""],
            low_memory=False,
        )
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        message = f"Could not parse source CSV at {source_path}: {exc}"
        raise DataLoadError(message) from exc


def load_validated_data(
    path: str | Path | None = None,
) -> tuple[pd.DataFrame, ValidationReport]:
    """Load source data and reject it when blocking validation errors exist."""
    frame = load_raw_data(path)
    report = validate_dataframe(frame)
    if not report.is_valid:
        raise DataValidationError(report)
    return frame, report
