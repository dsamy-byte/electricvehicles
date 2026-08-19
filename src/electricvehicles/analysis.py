"""Reproducible exploratory analysis for the cleaned EV population snapshot.

The functions in this module return presentation-neutral dataclasses. They do
not create charts, mutate data, or depend on Streamlit, which makes the same
calculations reusable in tests, command-line reports, and the future dashboard.

All time-oriented output describes the model-year composition of vehicles in a
current registration snapshot. It must not be interpreted as annual sales,
registrations, or a historical adoption series.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class CategoryResult:
    """Count and share for one non-null categorical value."""

    value: str
    count: int
    share: float


@dataclass(frozen=True)
class RangeResult:
    """Known electric-range coverage and distribution for one EV type."""

    ev_type_code: str
    vehicle_count: int
    known_range_count: int
    known_range_share: float
    mean_miles: float | None
    median_miles: float | None
    percentile_25_miles: float | None
    percentile_75_miles: float | None
    maximum_miles: int | None


@dataclass(frozen=True)
class ExploratoryAnalysis:
    """Serializable analytical summary of one cleaned population snapshot."""

    vehicle_count: int
    model_year_min: int
    model_year_max: int
    model_year_median: float
    make_count: int
    model_count: int
    county_count: int
    city_count: int
    recent_model_year_count: int
    recent_model_year_share: float
    top_10_make_share: float
    top_5_county_share: float
    model_years: tuple[CategoryResult, ...]
    vehicle_types: tuple[CategoryResult, ...]
    cafv_statuses: tuple[CategoryResult, ...]
    top_makes: tuple[CategoryResult, ...]
    top_models: tuple[CategoryResult, ...]
    top_counties: tuple[CategoryResult, ...]
    top_cities: tuple[CategoryResult, ...]
    range_by_vehicle_type: tuple[RangeResult, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible nested representation of the analysis."""
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize results with stable ordering for reproducible artifacts."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _share(count: int, total: int) -> float:
    """Return a six-decimal proportion while safely handling zero totals."""
    return round(count / total, 6) if total else 0.0


def category_breakdown(
    frame: pd.DataFrame,
    column: str,
    *,
    limit: int | None = None,
    sort_by_value: bool = False,
) -> tuple[CategoryResult, ...]:
    """Summarize non-null values in a categorical column.

    Args:
        frame: Clean dataframe containing ``column``.
        column: Categorical field to aggregate.
        limit: Optional maximum number of ranked results.
        sort_by_value: Sort labels ascending instead of ranking by frequency.
            This is used for naturally ordered model-year output.

    Returns:
        Immutable count/share rows. Shares use all dataframe rows as the
        denominator so missing values remain visible rather than renormalized.

    Raises:
        KeyError: If ``column`` is absent.
        ValueError: If ``limit`` is not positive when supplied.
    """
    if column not in frame:
        raise KeyError(f"Analysis column is missing: {column}")
    if limit is not None and limit <= 0:
        raise ValueError("Category result limit must be positive.")

    counts = frame[column].dropna().astype("string").value_counts()
    rows = [(str(value), int(count)) for value, count in counts.items()]
    if sort_by_value:
        # Numeric-looking labels, such as model years, sort numerically. Other
        # labels sort case-insensitively for deterministic output.
        def value_key(item: tuple[str, int]) -> tuple[int, float | str]:
            try:
                return (0, float(item[0]))
            except ValueError:
                return (1, item[0].casefold())

        rows.sort(key=value_key)
    else:
        rows.sort(key=lambda item: (-item[1], item[0].casefold()))
    if limit is not None:
        rows = rows[:limit]
    return tuple(
        CategoryResult(value=value, count=count, share=_share(count, len(frame)))
        for value, count in rows
    )


def _range_breakdown(frame: pd.DataFrame) -> tuple[RangeResult, ...]:
    """Describe known range by EV type without treating unknowns as zero."""
    results: list[RangeResult] = []
    for ev_type in sorted(frame["ev_type_code"].dropna().unique()):
        population = frame.loc[frame["ev_type_code"].eq(ev_type)]
        known = population["electric_range_miles"].dropna()
        known_count = len(known)
        if known_count:
            results.append(
                RangeResult(
                    ev_type_code=str(ev_type),
                    vehicle_count=len(population),
                    known_range_count=known_count,
                    known_range_share=_share(known_count, len(population)),
                    mean_miles=round(float(known.mean()), 2),
                    median_miles=float(known.median()),
                    percentile_25_miles=float(known.quantile(0.25)),
                    percentile_75_miles=float(known.quantile(0.75)),
                    maximum_miles=int(known.max()),
                )
            )
        else:
            results.append(
                RangeResult(
                    ev_type_code=str(ev_type),
                    vehicle_count=len(population),
                    known_range_count=0,
                    known_range_share=0.0,
                    mean_miles=None,
                    median_miles=None,
                    percentile_25_miles=None,
                    percentile_75_miles=None,
                    maximum_miles=None,
                )
            )
    return tuple(results)


def build_exploratory_analysis(frame: pd.DataFrame) -> ExploratoryAnalysis:
    """Calculate the approved exploratory views from cleaned vehicle data.

    Args:
        frame: Non-empty analysis-ready dataframe from ``clean_data``.

    Returns:
        Immutable summary containing population composition, concentration,
        categorical rankings, and known-range distributions.

    Raises:
        ValueError: If the dataframe is empty or lacks required clean columns.
    """
    required = {
        "model_year",
        "make",
        "model",
        "county",
        "city",
        "ev_type_code",
        "cafv_status",
        "electric_range_miles",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Exploratory analysis requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Exploratory analysis requires at least one vehicle.")

    model_years = frame["model_year"].dropna()
    if model_years.empty:
        raise ValueError("Exploratory analysis requires populated model years.")

    make_results = category_breakdown(frame, "make", limit=10)
    county_results = category_breakdown(frame, "county", limit=10)
    recent_count = int(frame["model_year"].ge(2021).sum())
    return ExploratoryAnalysis(
        vehicle_count=len(frame),
        model_year_min=int(model_years.min()),
        model_year_max=int(model_years.max()),
        model_year_median=float(model_years.median()),
        make_count=int(frame["make"].nunique(dropna=True)),
        model_count=int(frame["model"].nunique(dropna=True)),
        county_count=int(frame["county"].nunique(dropna=True)),
        city_count=int(frame["city"].nunique(dropna=True)),
        recent_model_year_count=recent_count,
        recent_model_year_share=_share(recent_count, len(frame)),
        top_10_make_share=round(sum(item.share for item in make_results), 6),
        top_5_county_share=round(sum(item.share for item in county_results[:5]), 6),
        model_years=category_breakdown(frame, "model_year", sort_by_value=True),
        vehicle_types=category_breakdown(frame, "ev_type_code"),
        cafv_statuses=category_breakdown(frame, "cafv_status"),
        top_makes=make_results,
        top_models=category_breakdown(frame, "model", limit=10),
        top_counties=county_results,
        top_cities=category_breakdown(frame, "city", limit=10),
        range_by_vehicle_type=_range_breakdown(frame),
    )
