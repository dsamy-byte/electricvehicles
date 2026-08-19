"""Range availability, known-range distributions, and CAFV page data.

The source uses zero when electric range has not been researched. Cleaning
preserves that raw value but exposes ``electric_range_miles`` as missing. This
module uses only the cleaned analytical field for statistics, always reports
coverage, and never imputes unknown values.

BEV and PHEV statistics remain separate because known-range coverage differs
materially between the two populations. Histograms are pre-aggregated into
fixed-width bins for predictable performance and to avoid sending vehicle-level
rows into the presentation layer.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from electricvehicles.analysis import CategoryResult, category_breakdown


@dataclass(frozen=True)
class RangeCoverage:
    """Known and unknown electric-range counts for one EV type."""

    ev_type_code: str
    vehicle_count: int
    known_count: int
    unknown_count: int
    known_share: float


@dataclass(frozen=True)
class RangeStatistics:
    """Known-value distribution and coverage for one EV type."""

    ev_type_code: str
    vehicle_count: int
    known_count: int
    known_share: float
    minimum_miles: int | None
    percentile_25_miles: float | None
    median_miles: float | None
    mean_miles: float | None
    percentile_75_miles: float | None
    maximum_miles: int | None


@dataclass(frozen=True)
class RangeBin:
    """Count of known-range vehicles within one inclusive mileage interval."""

    ev_type_code: str
    lower_miles: int
    upper_miles: int
    label: str
    count: int


@dataclass(frozen=True)
class RangeCafvData:
    """Immutable headline metrics and chart-ready range/CAFV records."""

    vehicle_count: int
    known_range_count: int
    known_range_share: float
    median_known_range: float | None
    eligible_count: int
    eligible_share: float
    unknown_cafv_count: int
    unknown_cafv_share: float
    coverage_by_type: tuple[RangeCoverage, ...]
    statistics_by_type: tuple[RangeStatistics, ...]
    range_bins: tuple[RangeBin, ...]
    cafv_statuses: tuple[CategoryResult, ...]
    bin_width_miles: int


def _share(count: int, total: int) -> float:
    """Return a six-decimal proportion for a non-empty denominator."""
    return round(count / total, 6)


def _statistics_by_type(frame: pd.DataFrame) -> tuple[RangeStatistics, ...]:
    """Calculate coverage and known-value summaries independently by EV type."""
    results: list[RangeStatistics] = []
    for ev_type in sorted(frame["ev_type_code"].dropna().unique()):
        population = frame.loc[frame["ev_type_code"].eq(ev_type)]
        known = population["electric_range_miles"].dropna()
        if known.empty:
            results.append(
                RangeStatistics(
                    ev_type_code=str(ev_type),
                    vehicle_count=len(population),
                    known_count=0,
                    known_share=0.0,
                    minimum_miles=None,
                    percentile_25_miles=None,
                    median_miles=None,
                    mean_miles=None,
                    percentile_75_miles=None,
                    maximum_miles=None,
                )
            )
            continue
        results.append(
            RangeStatistics(
                ev_type_code=str(ev_type),
                vehicle_count=len(population),
                known_count=len(known),
                known_share=_share(len(known), len(population)),
                minimum_miles=int(known.min()),
                percentile_25_miles=round(float(known.quantile(0.25)), 2),
                median_miles=round(float(known.median()), 2),
                mean_miles=round(float(known.mean()), 2),
                percentile_75_miles=round(float(known.quantile(0.75)), 2),
                maximum_miles=int(known.max()),
            )
        )
    return tuple(results)


def _range_bins(frame: pd.DataFrame, width: int) -> tuple[RangeBin, ...]:
    """Aggregate known range into fixed-width inclusive integer intervals."""
    known = frame.dropna(subset=["ev_type_code", "electric_range_miles"]).copy()
    if known.empty:
        return ()
    known["lower_miles"] = (
        known["electric_range_miles"].astype("int64") // width * width
    )
    grouped = (
        known.groupby(["ev_type_code", "lower_miles"], observed=True)
        .size()
        .sort_index()
    )
    return tuple(
        RangeBin(
            ev_type_code=str(ev_type),
            lower_miles=int(lower),
            upper_miles=int(lower) + width - 1,
            label=f"{int(lower)}-{int(lower) + width - 1}",
            count=int(count),
        )
        for (ev_type, lower), count in grouped.items()
    )


def build_range_cafv_data(
    frame: pd.DataFrame, *, bin_width_miles: int = 10
) -> RangeCafvData:
    """Calculate coverage-aware range and CAFV results for filtered data.

    Args:
        frame: Non-empty analysis-ready dataframe after global filters.
        bin_width_miles: Positive integer width for known-range histogram bins.

    Returns:
        Immutable headline metrics, per-type statistics, aggregated histogram
        bins, and all populated CAFV categories.

    Raises:
        ValueError: If required clean fields are missing, the frame is empty,
            EV type is entirely missing, or the bin width is invalid.
    """
    required = {
        "dol_vehicle_id",
        "ev_type_code",
        "electric_range_miles",
        "cafv_status",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Range and CAFV analysis requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Range and CAFV analysis requires filtered vehicles.")
    if not isinstance(bin_width_miles, int) or bin_width_miles <= 0:
        raise ValueError("Range bin width must be a positive integer.")
    if frame["ev_type_code"].dropna().empty:
        raise ValueError("Range analysis requires at least one populated EV type.")

    vehicle_count = int(frame["dol_vehicle_id"].nunique(dropna=True))
    known = frame["electric_range_miles"].dropna()
    known_count = len(known)
    eligible_count = int(frame["cafv_status"].eq("Eligible").sum())
    unknown_cafv_count = int(frame["cafv_status"].eq("Unknown").sum())
    statistics = _statistics_by_type(frame)
    coverage = tuple(
        RangeCoverage(
            ev_type_code=item.ev_type_code,
            vehicle_count=item.vehicle_count,
            known_count=item.known_count,
            unknown_count=item.vehicle_count - item.known_count,
            known_share=item.known_share,
        )
        for item in statistics
    )
    return RangeCafvData(
        vehicle_count=vehicle_count,
        known_range_count=known_count,
        known_range_share=_share(known_count, vehicle_count),
        median_known_range=(
            round(float(known.median()), 2) if not known.empty else None
        ),
        eligible_count=eligible_count,
        eligible_share=_share(eligible_count, vehicle_count),
        unknown_cafv_count=unknown_cafv_count,
        unknown_cafv_share=_share(unknown_cafv_count, vehicle_count),
        coverage_by_type=coverage,
        statistics_by_type=statistics,
        range_bins=_range_bins(frame, bin_width_miles),
        cafv_statuses=category_breakdown(frame, "cafv_status"),
        bin_width_miles=bin_width_miles,
    )
