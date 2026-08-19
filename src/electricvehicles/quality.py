"""Machine-readable data-quality profiling and baseline comparison.

The quality layer consumes the analysis-ready dataframe created by
``cleaning.py``. It does not repair data. Instead, it makes completeness,
uniqueness, consistency, and snapshot drift visible through documented Python
objects that can be serialized to JSON or rendered by the Streamlit app.

Baseline checks are intentionally tolerant of normal source refreshes. They
detect material drift; they do not require a future dataset to have the same
row count or distributions as the initial snapshot.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from electricvehicles.config import PROJECT_ROOT
from electricvehicles.validation import ValidationReport

DEFAULT_BASELINE_PATH = PROJECT_ROOT / "config" / "quality_baseline.json"


@dataclass(frozen=True)
class ColumnQuality:
    """Completeness and cardinality metrics for one cleaned column."""

    missing_count: int
    missing_rate: float
    unique_count: int


@dataclass(frozen=True)
class BaselineCheck:
    """Result of comparing one observed metric with a baseline threshold."""

    metric: str
    observed: float | int
    expectation: str
    passed: bool


@dataclass(frozen=True)
class DataQualityReport:
    """Serializable quality summary for one cleaned dataset snapshot.

    Counts and rates are stored separately so consumers never need to infer a
    denominator. ``baseline_checks`` can contain failures without making the
    validated dataset unusable; callers decide whether drift blocks deployment.
    """

    row_count: int
    column_count: int
    exact_duplicate_rows: int
    duplicate_vehicle_ids: int
    unknown_range_count: int
    unknown_range_rate: float
    complete_coordinate_count: int
    complete_coordinate_rate: float
    washington_vehicle_count: int
    washington_share: float
    columns: dict[str, ColumnQuality]
    validation_warnings: tuple[str, ...]
    baseline_version: int
    baseline_checks: tuple[BaselineCheck, ...]

    @property
    def is_within_baseline(self) -> bool:
        """Return whether every configured snapshot-drift check passed."""
        return all(check.passed for check in self.baseline_checks)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of the complete report."""
        result = asdict(self)
        result["is_within_baseline"] = self.is_within_baseline
        return result

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the report with stable key order for reproducible output."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class QualityBaselineError(ValueError):
    """Raised when the versioned baseline cannot be read or interpreted."""


def load_quality_baseline(path: str | Path | None = None) -> dict[str, Any]:
    """Load and minimally validate the versioned quality baseline.

    Args:
        path: Optional JSON path. Relative paths resolve from the project root.

    Returns:
        Parsed baseline configuration.

    Raises:
        QualityBaselineError: If the file is missing, malformed, or lacks the
            supported baseline version and required sections.
    """
    baseline_path = Path(path) if path is not None else DEFAULT_BASELINE_PATH
    if not baseline_path.is_absolute():
        baseline_path = PROJECT_ROOT / baseline_path
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QualityBaselineError(
            f"Could not load quality baseline at {baseline_path}: {exc}"
        ) from exc

    required = {
        "version",
        "row_count",
        "maximum_missing_rates",
        "maximum_exact_duplicate_rows",
        "maximum_duplicate_vehicle_ids",
        "unknown_range_rate",
        "washington_share",
    }
    missing = sorted(required - set(baseline))
    if missing or baseline.get("version") != 1:
        raise QualityBaselineError(
            "Quality baseline must use version 1 and include all required "
            f"sections. Missing: {missing or 'none'}."
        )
    return baseline


def _rate(count: int, total: int) -> float:
    """Calculate a safe, consistently rounded proportion."""
    return round(count / total, 6) if total else 0.0


def _column_profiles(frame: pd.DataFrame) -> dict[str, ColumnQuality]:
    """Profile missingness and non-null cardinality for every clean column."""
    total = len(frame)
    profiles: dict[str, ColumnQuality] = {}
    for column in frame.columns:
        missing_count = int(frame[column].isna().sum())
        profiles[column] = ColumnQuality(
            missing_count=missing_count,
            missing_rate=_rate(missing_count, total),
            unique_count=int(frame[column].nunique(dropna=True)),
        )
    return profiles


def _range_check(
    metric: str,
    observed: float,
    expected: float,
    tolerance: float,
) -> BaselineCheck:
    """Compare a rate with an inclusive expected ± tolerance interval."""
    lower = expected - tolerance
    upper = expected + tolerance
    return BaselineCheck(
        metric=metric,
        observed=observed,
        expectation=f"between {lower:.6f} and {upper:.6f}",
        passed=lower <= observed <= upper,
    )


def _compare_baseline(
    *,
    baseline: dict[str, Any],
    row_count: int,
    exact_duplicates: int,
    duplicate_ids: int,
    unknown_range_rate: float,
    washington_share: float,
    columns: dict[str, ColumnQuality],
) -> tuple[BaselineCheck, ...]:
    """Evaluate observed snapshot metrics against all configured thresholds."""
    checks: list[BaselineCheck] = []
    row_config = baseline["row_count"]
    expected_rows = int(row_config["expected"])
    row_tolerance = float(row_config["relative_tolerance"])
    lower_rows = round(expected_rows * (1 - row_tolerance))
    upper_rows = round(expected_rows * (1 + row_tolerance))
    checks.append(
        BaselineCheck(
            metric="row_count",
            observed=row_count,
            expectation=f"between {lower_rows} and {upper_rows}",
            passed=lower_rows <= row_count <= upper_rows,
        )
    )

    checks.extend(
        (
            BaselineCheck(
                metric="exact_duplicate_rows",
                observed=exact_duplicates,
                expectation=(f"at most {baseline['maximum_exact_duplicate_rows']}"),
                passed=exact_duplicates
                <= int(baseline["maximum_exact_duplicate_rows"]),
            ),
            BaselineCheck(
                metric="duplicate_vehicle_ids",
                observed=duplicate_ids,
                expectation=(f"at most {baseline['maximum_duplicate_vehicle_ids']}"),
                passed=duplicate_ids <= int(baseline["maximum_duplicate_vehicle_ids"]),
            ),
        )
    )

    for column, maximum in baseline["maximum_missing_rates"].items():
        observed = columns[column].missing_rate
        checks.append(
            BaselineCheck(
                metric=f"missing_rate.{column}",
                observed=observed,
                expectation=f"at most {float(maximum):.6f}",
                passed=observed <= float(maximum),
            )
        )

    range_config = baseline["unknown_range_rate"]
    checks.append(
        _range_check(
            "unknown_range_rate",
            unknown_range_rate,
            float(range_config["expected"]),
            float(range_config["absolute_tolerance"]),
        )
    )
    state_config = baseline["washington_share"]
    checks.append(
        _range_check(
            "washington_share",
            washington_share,
            float(state_config["expected"]),
            float(state_config["absolute_tolerance"]),
        )
    )
    return tuple(checks)


def build_quality_report(
    frame: pd.DataFrame,
    validation_report: ValidationReport,
    *,
    baseline: dict[str, Any] | None = None,
) -> DataQualityReport:
    """Measure a cleaned dataframe and compare it with the quality baseline.

    Args:
        frame: Analysis-ready dataframe returned by ``clean_data``.
        validation_report: Report produced while loading the same snapshot.
        baseline: Optional parsed baseline, primarily useful for tests or
            controlled experiments. The versioned project baseline is default.

    Returns:
        An immutable report suitable for JSON export or dashboard rendering.

    Raises:
        ValueError: If required clean columns are absent or the dataframe is
            empty, which indicates misuse of this layer.
    """
    required_columns = {
        "dol_vehicle_id",
        "electric_range_miles",
        "longitude",
        "latitude",
        "is_washington",
    }
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"Quality reporting requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Quality reporting requires at least one data row.")

    active_baseline = baseline or load_quality_baseline()
    row_count = len(frame)
    columns = _column_profiles(frame)
    exact_duplicates = int(frame.duplicated().sum())
    duplicate_ids = int(frame["dol_vehicle_id"].duplicated().sum())
    unknown_range = int(frame["electric_range_miles"].isna().sum())
    complete_coordinates = int(
        (frame["longitude"].notna() & frame["latitude"].notna()).sum()
    )
    washington_count = int(frame["is_washington"].fillna(False).sum())
    unknown_rate = _rate(unknown_range, row_count)
    washington_rate = _rate(washington_count, row_count)

    checks = _compare_baseline(
        baseline=active_baseline,
        row_count=row_count,
        exact_duplicates=exact_duplicates,
        duplicate_ids=duplicate_ids,
        unknown_range_rate=unknown_rate,
        washington_share=washington_rate,
        columns=columns,
    )
    return DataQualityReport(
        row_count=row_count,
        column_count=len(frame.columns),
        exact_duplicate_rows=exact_duplicates,
        duplicate_vehicle_ids=duplicate_ids,
        unknown_range_count=unknown_range,
        unknown_range_rate=unknown_rate,
        complete_coordinate_count=complete_coordinates,
        complete_coordinate_rate=_rate(complete_coordinates, row_count),
        washington_vehicle_count=washington_count,
        washington_share=washington_rate,
        columns=columns,
        validation_warnings=tuple(str(issue) for issue in validation_report.warnings),
        baseline_version=int(active_baseline["version"]),
        baseline_checks=checks,
    )


def write_quality_report(report: DataQualityReport, path: str | Path) -> Path:
    """Write a report as UTF-8 JSON and return its resolved output path.

    Parent directories are created for an explicit output path. Generated
    reports are excluded from Git because they belong to a particular source
    snapshot; the baseline configuration remains version controlled.
    """
    output = Path(path)
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{report.to_json()}\n", encoding="utf-8")
    return output.resolve()
