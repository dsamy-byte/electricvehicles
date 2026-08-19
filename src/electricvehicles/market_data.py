"""Presentation-neutral market composition for the Makes & Models page.

This module defines manufacturer/model identity and every denominator used by
the market page. A model is grouped by ``(make, model)`` rather than model label
alone because different manufacturers can reuse the same label. Rankings use a
stable alphabetical tie-break after descending vehicle count.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MarketRank:
    """One ranked make or make/model combination.

    ``share`` and ``cumulative_share`` use the complete filtered vehicle
    population as denominator, so missing categories are never redistributed
    across populated categories.
    """

    rank: int
    label: str
    make: str
    model: str | None
    count: int
    share: float
    cumulative_share: float


@dataclass(frozen=True)
class HeatmapCell:
    """Vehicle count for one leading-make and model-year intersection."""

    make: str
    model_year: int
    count: int


@dataclass(frozen=True)
class MarketData:
    """Immutable metrics and chart-ready records for a filtered population."""

    vehicle_count: int
    make_count: int
    make_model_count: int
    leading_make: str
    leading_make_count: int
    leading_make_share: float
    top_10_make_share: float
    make_rankings: tuple[MarketRank, ...]
    model_rankings: tuple[MarketRank, ...]
    heatmap_cells: tuple[HeatmapCell, ...]
    heatmap_makes: tuple[str, ...]
    model_years: tuple[int, ...]


def _rank_counts(
    counts: pd.Series, total: int, *, models: bool
) -> tuple[MarketRank, ...]:
    """Convert grouped counts into deterministic ranks and cumulative shares."""
    if models:
        rows = [
            (str(make), str(model), int(count))
            for (make, model), count in counts.items()
        ]
        rows.sort(key=lambda item: (-item[2], item[0].casefold(), item[1].casefold()))
    else:
        rows = [(str(make), None, int(count)) for make, count in counts.items()]
        rows.sort(key=lambda item: (-item[2], item[0].casefold()))

    cumulative = 0
    results: list[MarketRank] = []
    for rank, (make, model, count) in enumerate(rows, start=1):
        cumulative += count
        label = make if model is None else f"{model} — {make}"
        results.append(
            MarketRank(
                rank=rank,
                label=label,
                make=make,
                model=model,
                count=count,
                share=round(count / total, 6),
                cumulative_share=round(cumulative / total, 6),
            )
        )
    return tuple(results)


def _build_heatmap(
    frame: pd.DataFrame,
    leading_makes: tuple[str, ...],
) -> tuple[tuple[HeatmapCell, ...], tuple[int, ...]]:
    """Create a complete make × model-year grid, including zero-count cells."""
    model_years = tuple(
        int(year) for year in sorted(frame["model_year"].dropna().unique())
    )
    selected = frame.loc[frame["make"].isin(leading_makes)]
    counts = selected.groupby(["make", "model_year"], observed=True).size()
    cells = tuple(
        HeatmapCell(
            make=make,
            model_year=year,
            count=int(counts.get((make, year), 0)),
        )
        for make in leading_makes
        for year in model_years
    )
    return cells, model_years


def build_market_data(
    frame: pd.DataFrame, *, heatmap_make_limit: int = 10
) -> MarketData:
    """Calculate rankings, concentration, and heatmap values for market views.

    Args:
        frame: Non-empty analysis-ready dataframe after global filters.
        heatmap_make_limit: Positive maximum number of leading makes included in
            the heatmap grid. Rankings always retain every make/model so page
            controls can choose their own visible Top N values.

    Returns:
        Immutable market metrics, complete rankings, and heatmap cells.

    Raises:
        ValueError: If required clean columns are missing, the frame is empty,
            populated make/model-year values are absent, or the limit is invalid.
    """
    required = {"dol_vehicle_id", "make", "model", "model_year"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Market analysis requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Market analysis requires at least one filtered vehicle.")
    if heatmap_make_limit <= 0:
        raise ValueError("Heatmap make limit must be positive.")

    categorized = frame.dropna(subset=["make", "model"])
    if categorized.empty:
        raise ValueError("Market analysis requires populated make and model values.")
    if frame["model_year"].dropna().empty:
        raise ValueError("Market analysis requires populated model years.")

    vehicle_count = int(frame["dol_vehicle_id"].nunique(dropna=True))
    make_counts = categorized.groupby("make", observed=True).size()
    model_counts = categorized.groupby(["make", "model"], observed=True).size()
    make_rankings = _rank_counts(make_counts, vehicle_count, models=False)
    model_rankings = _rank_counts(model_counts, vehicle_count, models=True)
    leading_makes = tuple(result.make for result in make_rankings[:heatmap_make_limit])
    heatmap_cells, model_years = _build_heatmap(frame, leading_makes)
    top_ten_share = round(sum(result.share for result in make_rankings[:10]), 6)
    leader = make_rankings[0]
    return MarketData(
        vehicle_count=vehicle_count,
        make_count=len(make_rankings),
        make_model_count=len(model_rankings),
        leading_make=leader.make,
        leading_make_count=leader.count,
        leading_make_share=leader.share,
        top_10_make_share=top_ten_share,
        make_rankings=make_rankings,
        model_rankings=model_rankings,
        heatmap_cells=heatmap_cells,
        heatmap_makes=leading_makes,
        model_years=model_years,
    )
