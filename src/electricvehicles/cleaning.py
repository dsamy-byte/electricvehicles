"""Deterministic preparation of validated electric-vehicle source data.

This module is intentionally separate from ingestion and validation:

* ingestion preserves the CSV representation;
* validation decides whether the source is safe to interpret; and
* cleaning creates analysis-ready names, types, and derived fields.

No function writes files or mutates its input dataframe. Transformations are
policy-driven by ``docs/DATA_CONTRACT.md`` and are designed to be idempotent at
the pipeline boundary: callers always provide the original source schema and
receive a new dataframe with the documented clean schema.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from electricvehicles.data_contract import (
    CAFV_DISPLAY_LABELS,
    COLUMN_RENAMES,
    EV_TYPE_CODES,
)
from electricvehicles.ingestion import load_validated_data
from electricvehicles.validation import (
    POINT_PATTERN,
    DataValidationError,
    ValidationReport,
    validate_dataframe,
)


def _clean_text(series: pd.Series, *, uppercase: bool = False) -> pd.Series:
    """Return nullable text with surrounding/repeated whitespace normalized.

    Missing values remain ``pd.NA``. Internal whitespace is collapsed because
    accidental repeated spaces would otherwise fragment dashboard categories.
    Case is preserved by default to avoid damaging proper place names.
    """
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True).replace("", pd.NA)
    return cleaned.str.upper() if uppercase else cleaned


def _nullable_integer(series: pd.Series) -> pd.Series:
    """Convert a previously validated integer-like series to pandas ``Int64``."""
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def _parse_locations(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Extract longitude and latitude from validated WKT point strings.

    Invalid or absent points become missing coordinates. Validation reports
    invalid points before this function runs, so silently missing coordinates
    here cannot make a bad source pass validation.
    """
    coordinates = series.astype("string").str.extract(POINT_PATTERN)
    longitude = pd.to_numeric(coordinates[0], errors="coerce").astype("Float64")
    latitude = pd.to_numeric(coordinates[1], errors="coerce").astype("Float64")
    return longitude, latitude


def clean_data(frame: pd.DataFrame, *, validate: bool = True) -> pd.DataFrame:
    """Create an analysis-ready copy of a raw source dataframe.

    Args:
        frame: Dataframe with the exact 16-column source schema. By default it
            is validated before transformation.
        validate: Disable only when the caller has just obtained ``frame`` from
            :func:`load_validated_data`; this avoids duplicate full-data work.

    Returns:
        A new dataframe with snake-case columns, deliberate nullable types,
        parsed coordinates, and documented display fields. The input dataframe
        is never modified.

    Raises:
        DataValidationError: If ``validate`` is true and a blocking source-data
            rule fails.
    """
    if validate:
        report = validate_dataframe(frame)
        if not report.is_valid:
            raise DataValidationError(report)

    # Deep copy makes the non-mutation guarantee explicit even if pandas later
    # changes copy-on-write defaults or a transformation uses in-place logic.
    cleaned = frame.copy(deep=True).rename(columns=COLUMN_RENAMES)

    text_columns = (
        "vin_prefix",
        "county",
        "city",
        "state",
        "postal_code",
        "make",
        "model",
        "ev_type",
        "cafv_eligibility",
        "dol_vehicle_id",
        "vehicle_location",
        "electric_utility",
        "census_tract_2020",
    )
    for column in text_columns:
        cleaned[column] = _clean_text(cleaned[column])

    # These source domains are conventionally uppercase and safe to normalize;
    # city/county/model names intentionally retain publisher casing.
    for column in ("vin_prefix", "state", "make"):
        cleaned[column] = cleaned[column].str.upper()

    four_digit_postal = cleaned["postal_code"].str.fullmatch(r"\d{4}", na=False)
    cleaned.loc[four_digit_postal, "postal_code"] = (
        "0" + cleaned.loc[four_digit_postal, "postal_code"]
    )

    cleaned["model_year"] = _nullable_integer(cleaned["model_year"])
    cleaned["legislative_district"] = _nullable_integer(cleaned["legislative_district"])
    cleaned["electric_range_raw"] = _nullable_integer(cleaned["electric_range_raw"])

    # Zero is retained in the audit field but excluded from range statistics.
    # The publisher uses it when battery range has not been researched.
    cleaned["electric_range_miles"] = cleaned["electric_range_raw"].mask(
        cleaned["electric_range_raw"].eq(0)
    )

    cleaned["ev_type_code"] = cleaned["ev_type"].map(EV_TYPE_CODES).astype("string")
    cleaned["cafv_status"] = (
        cleaned["cafv_eligibility"].map(CAFV_DISPLAY_LABELS).astype("string")
    )
    cleaned["is_washington"] = cleaned["state"].eq("WA").astype("boolean")
    cleaned["longitude"], cleaned["latitude"] = _parse_locations(
        cleaned["vehicle_location"]
    )

    return cleaned


def load_clean_data(
    path: str | Path | None = None,
) -> tuple[pd.DataFrame, ValidationReport]:
    """Load, validate, and clean a source CSV through the supported pipeline.

    Args:
        path: Optional explicit CSV path. When omitted, configuration follows
            the precedence documented by :func:`electricvehicles.config.get_data_path`.

    Returns:
        A pair containing the cleaned dataframe and the validation report. The
        report carries non-blocking warnings that callers should expose in data
        quality views or logs.

    Raises:
        DataLoadError: Indirectly from ingestion when the file cannot be read.
        DataValidationError: Indirectly when blocking contract rules fail.
    """
    raw_data, report = load_validated_data(path)
    return clean_data(raw_data, validate=False), report
