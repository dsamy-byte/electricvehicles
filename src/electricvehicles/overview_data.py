"""Presentation-neutral metrics and series for the dashboard Overview page.

The Overview renderer should not calculate business metrics directly. This
module centralizes every denominator and aggregation so definitions remain
testable, reusable, and consistent with ``docs/DASHBOARD_SPEC.md``.

All shares use the filtered vehicle population as their denominator. Unknown
range and CAFV values therefore remain visible rather than being silently
excluded from headline percentages.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from electricvehicles.analysis import CategoryResult, category_breakdown


@dataclass(frozen=True)
class OverviewData:
    """Immutable metrics and chart series for one filtered population.

    Attributes:
        vehicle_count: Distinct DOL vehicle identifiers after filtering.
        bev_count: Filtered vehicles classified as BEV.
        bev_share: BEV count divided by ``vehicle_count``.
        median_model_year: Median populated model year.
        known_range_count: Vehicles with researched, non-zero electric range.
        known_range_share: Known-range count divided by ``vehicle_count``.
        eligible_count: Vehicles whose CAFV display status is Eligible.
        eligible_share: Eligible count divided by ``vehicle_count``; unknown
            statuses remain in the denominator.
        model_years: Chronological count/share series for the composition chart.
        vehicle_types: Ranked EV-type count/share series.
        top_makes: Leading make count/share series with deterministic tie order.
    """

    vehicle_count: int
    bev_count: int
    bev_share: float
    median_model_year: float
    known_range_count: int
    known_range_share: float
    eligible_count: int
    eligible_share: float
    model_years: tuple[CategoryResult, ...]
    vehicle_types: tuple[CategoryResult, ...]
    top_makes: tuple[CategoryResult, ...]


def _share(count: int, total: int) -> float:
    """Return a six-decimal proportion for a non-empty population."""
    return round(count / total, 6)


def build_overview_data(
    frame: pd.DataFrame, *, top_make_limit: int = 5
) -> OverviewData:
    """Calculate all Overview metrics from a filtered clean dataframe.

    Args:
        frame: Non-empty, analysis-ready filtered vehicle dataframe.
        top_make_limit: Positive number of makes to retain for the overview
            ranking. The detailed market page uses its own larger controls.

    Returns:
        Documented immutable metrics and chart series.

    Raises:
        ValueError: If the frame is empty, required clean columns are absent,
            model year is entirely missing, or ``top_make_limit`` is invalid.
    """
    required = {
        "dol_vehicle_id",
        "ev_type_code",
        "model_year",
        "electric_range_miles",
        "cafv_status",
        "make",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Overview requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Overview requires at least one filtered vehicle.")
    if top_make_limit <= 0:
        raise ValueError("Overview make limit must be positive.")

    model_years = frame["model_year"].dropna()
    if model_years.empty:
        raise ValueError("Overview requires at least one populated model year.")

    # Validation guarantees DOL IDs are unique, but nunique states the metric's
    # entity definition explicitly and protects it from future joins.
    vehicle_count = int(frame["dol_vehicle_id"].nunique(dropna=True))
    bev_count = int(frame["ev_type_code"].eq("BEV").sum())
    known_range_count = int(frame["electric_range_miles"].notna().sum())
    eligible_count = int(frame["cafv_status"].eq("Eligible").sum())
    return OverviewData(
        vehicle_count=vehicle_count,
        bev_count=bev_count,
        bev_share=_share(bev_count, vehicle_count),
        median_model_year=float(model_years.median()),
        known_range_count=known_range_count,
        known_range_share=_share(known_range_count, vehicle_count),
        eligible_count=eligible_count,
        eligible_share=_share(eligible_count, vehicle_count),
        model_years=category_breakdown(frame, "model_year", sort_by_value=True),
        vehicle_types=category_breakdown(frame, "ev_type_code"),
        top_makes=category_breakdown(frame, "make", limit=top_make_limit),
    )
