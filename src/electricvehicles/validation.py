"""Validation rules for raw Electric Vehicle Population Data."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from electricvehicles.data_contract import (
    CAFV_LABELS,
    EV_TYPES,
    REQUIRED_VALUE_COLUMNS,
    SOURCE_COLUMNS,
)

VIN_PREFIX_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{10}$")
STATE_PATTERN = re.compile(r"^[A-Z]{2}$")
POSTAL_PATTERN = re.compile(r"^\d{4,5}$")
CENSUS_TRACT_PATTERN = re.compile(r"^\d{11}$")
POINT_PATTERN = re.compile(r"^POINT \((-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)\)$")


@dataclass(frozen=True)
class ValidationIssue:
    """One actionable contract violation or quality concern."""

    code: str
    message: str
    count: int | None = None

    def __str__(self) -> str:
        suffix = f" ({self.count:,} rows)" if self.count is not None else ""
        return f"[{self.code}] {self.message}{suffix}"


@dataclass
class ValidationReport:
    """Collection of blocking errors and non-blocking warnings."""

    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def error(self, code: str, message: str, count: int | None = None) -> None:
        self.errors.append(ValidationIssue(code, message, count))

    def warn(self, code: str, message: str, count: int | None = None) -> None:
        self.warnings.append(ValidationIssue(code, message, count))


class DataValidationError(ValueError):
    """Raised when source data violates a blocking contract rule."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        details = "\n".join(f"- {issue}" for issue in report.errors)
        super().__init__(f"Source data failed validation:\n{details}")


def _blank_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype("string").str.strip().eq("")


def _present_text(series: pd.Series) -> pd.Series:
    return series.loc[~_blank_mask(series)].astype("string").str.strip()


def _validate_integer_column(
    frame: pd.DataFrame,
    column: str,
    report: ValidationReport,
    *,
    nullable: bool,
) -> pd.Series:
    blank = _blank_mask(frame[column])
    values = pd.to_numeric(frame[column].where(~blank), errors="coerce")
    invalid = (~blank) & (values.isna() | values.mod(1).ne(0))
    if invalid.any():
        report.error(
            "invalid_integer",
            f"{column!r} must contain integer values.",
            int(invalid.sum()),
        )
    if not nullable and blank.any():
        report.error(
            "missing_required_value",
            f"{column!r} cannot be blank.",
            int(blank.sum()),
        )
    return values


def validate_dataframe(frame: pd.DataFrame) -> ValidationReport:
    """Validate a raw dataframe against the documented source contract."""
    report = ValidationReport()

    if tuple(frame.columns) != SOURCE_COLUMNS:
        report.error(
            "invalid_columns",
            "Columns or column order do not match the documented source schema.",
        )
        return report
    if frame.empty:
        report.error("empty_dataset", "The source file contains no data rows.")
        return report

    for column in REQUIRED_VALUE_COLUMNS:
        blank_count = int(_blank_mask(frame[column]).sum())
        if blank_count:
            report.error(
                "missing_required_value",
                f"{column!r} cannot be blank.",
                blank_count,
            )

    vin = frame["VIN (1-10)"].astype("string").str.strip()
    invalid_vin = ~vin.str.fullmatch(VIN_PREFIX_PATTERN, na=False)
    if invalid_vin.any():
        report.error(
            "invalid_vin_prefix",
            "VIN (1-10) must contain exactly 10 uppercase VIN characters.",
            int(invalid_vin.sum()),
        )

    model_year = _validate_integer_column(frame, "Model Year", report, nullable=False)
    implausible_year = model_year.notna() & ~model_year.between(
        1886, date.today().year + 2
    )
    if implausible_year.any():
        report.error(
            "implausible_model_year",
            f"Model Year must be between 1886 and {date.today().year + 2}.",
            int(implausible_year.sum()),
        )

    electric_range = _validate_integer_column(
        frame, "Electric Range", report, nullable=True
    )
    negative_range = electric_range.notna() & electric_range.lt(0)
    if negative_range.any():
        report.error(
            "negative_electric_range",
            "Electric Range cannot be negative.",
            int(negative_range.sum()),
        )

    vehicle_id = _validate_integer_column(
        frame, "DOL Vehicle ID", report, nullable=False
    )
    non_positive_id = vehicle_id.notna() & vehicle_id.le(0)
    if non_positive_id.any():
        report.error(
            "non_positive_vehicle_id",
            "DOL Vehicle ID must be positive.",
            int(non_positive_id.sum()),
        )
    duplicate_id = vehicle_id.notna() & vehicle_id.duplicated(keep=False)
    if duplicate_id.any():
        report.error(
            "duplicate_vehicle_id",
            "DOL Vehicle ID must be unique within a snapshot.",
            int(duplicate_id.sum()),
        )

    _validate_allowed_values(frame, "Electric Vehicle Type", EV_TYPES, report)
    _validate_allowed_values(
        frame,
        "Clean Alternative Fuel Vehicle (CAFV) Eligibility",
        CAFV_LABELS,
        report,
    )
    _validate_quality_warnings(frame, report)
    return report


def _validate_allowed_values(
    frame: pd.DataFrame,
    column: str,
    allowed: frozenset[str],
    report: ValidationReport,
) -> None:
    values = _present_text(frame[column])
    unexpected = sorted(set(values) - allowed)
    if unexpected:
        preview = ", ".join(repr(value) for value in unexpected[:5])
        report.error(
            "unexpected_category",
            f"{column!r} contains unreviewed values: {preview}.",
            int(values.isin(unexpected).sum()),
        )


def _validate_quality_warnings(frame: pd.DataFrame, report: ValidationReport) -> None:
    optional_columns = set(SOURCE_COLUMNS) - set(REQUIRED_VALUE_COLUMNS)
    for column in sorted(optional_columns):
        count = int(_blank_mask(frame[column]).sum())
        if count:
            report.warn(
                "missing_optional_value",
                f"{column!r} contains blank values.",
                count,
            )

    state = _present_text(frame["State"])
    bad_state = ~state.str.fullmatch(STATE_PATTERN, na=False)
    if bad_state.any():
        report.warn(
            "invalid_state_format",
            "State should contain a two-character uppercase code.",
            int(bad_state.sum()),
        )

    postal = _present_text(frame["Postal Code"])
    bad_postal = ~postal.str.fullmatch(POSTAL_PATTERN, na=False)
    if bad_postal.any():
        report.warn(
            "invalid_postal_format",
            "Postal Code should contain four or five digits before cleaning.",
            int(bad_postal.sum()),
        )

    tract = _present_text(frame["2020 Census Tract"])
    bad_tract = ~tract.str.fullmatch(CENSUS_TRACT_PATTERN, na=False)
    if bad_tract.any():
        report.warn(
            "invalid_census_tract",
            "2020 Census Tract should contain exactly 11 digits.",
            int(bad_tract.sum()),
        )

    district_text = _present_text(frame["Legislative District"])
    district = pd.to_numeric(district_text, errors="coerce")
    bad_district = district.isna() | district.mod(1).ne(0) | ~district.between(1, 49)
    if bad_district.any():
        report.warn(
            "invalid_legislative_district",
            "Legislative District should be an integer from 1 through 49.",
            int(bad_district.sum()),
        )

    locations = _present_text(frame["Vehicle Location"])
    invalid_location_count = 0
    for location in locations:
        match = POINT_PATTERN.fullmatch(location)
        if match is None:
            invalid_location_count += 1
            continue
        longitude, latitude = (float(value) for value in match.groups())
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            invalid_location_count += 1
    if invalid_location_count:
        report.warn(
            "invalid_vehicle_location",
            "Vehicle Location must be a bounded WKT POINT (longitude latitude).",
            invalid_location_count,
        )
