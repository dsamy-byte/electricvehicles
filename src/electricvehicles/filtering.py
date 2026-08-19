"""Presentation-independent filtering for analytical dashboard pages.

Filter semantics live outside Streamlit so every page uses the same ordering,
defaults, and interpretation. Empty categorical selections mean “all values.”
The Data Quality page intentionally bypasses this module and describes the
complete source snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FilterSelection:
    """Immutable global filter values selected by a dashboard user.

    Attributes:
        washington_only: Restrict records to normalized state code ``WA``.
        model_year_min: Inclusive lower model-year bound.
        model_year_max: Inclusive upper model-year bound.
        ev_types: Selected short codes. An empty tuple means all available.
        makes: Selected makes. An empty tuple means all available.
        counties: Selected source county labels. Empty means all available.
        cafv_statuses: Selected display statuses. Empty means all available.
    """

    washington_only: bool
    model_year_min: int
    model_year_max: int
    ev_types: tuple[str, ...] = ()
    makes: tuple[str, ...] = ()
    counties: tuple[str, ...] = ()
    cafv_statuses: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Reject inverted year ranges before they reach page calculations."""
        if self.model_year_min > self.model_year_max:
            raise ValueError("Minimum model year cannot exceed maximum model year.")


FILTER_COLUMNS = {
    "ev_types": "ev_type_code",
    "makes": "make",
    "counties": "county",
    "cafv_statuses": "cafv_status",
}


def apply_filters(frame: pd.DataFrame, selection: FilterSelection) -> pd.DataFrame:
    """Return a filtered copy using the documented global filter precedence.

    Args:
        frame: Clean analysis-ready dataframe.
        selection: Immutable values from the shared sidebar.

    Returns:
        A row-filtered copy with the original index retained. Returning a copy
        prevents page code from accidentally mutating cached application data.

    Raises:
        ValueError: If required clean filter columns are missing.
    """
    required = {"state", "model_year", *FILTER_COLUMNS.values()}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Filtering requires clean columns: {missing}")

    mask = frame["model_year"].between(
        selection.model_year_min, selection.model_year_max
    )
    if selection.washington_only:
        mask &= frame["state"].eq("WA")
    for attribute, column in FILTER_COLUMNS.items():
        values = getattr(selection, attribute)
        if values:
            mask &= frame[column].isin(values)
    return frame.loc[mask].copy()


def available_values(frame: pd.DataFrame, column: str) -> tuple[str, ...]:
    """Return deterministic, case-insensitive options from populated values."""
    if column not in frame:
        raise KeyError(f"Filter option column is missing: {column}")
    values = (str(value) for value in frame[column].dropna().unique())
    return tuple(sorted(values, key=str.casefold))


def describe_filters(selection: FilterSelection) -> str:
    """Build the compact, human-readable context shown on analytical pages."""

    def selected(values: tuple[str, ...], noun: str) -> str:
        if not values:
            return f"All {noun}"
        if len(values) <= 2:
            return ", ".join(values)
        return f"{len(values)} {noun} selected"

    scope = "Washington only" if selection.washington_only else "All source states"
    parts = (
        scope,
        f"Model years {selection.model_year_min}-{selection.model_year_max}",
        selected(selection.ev_types, "EV types"),
        selected(selection.makes, "makes"),
        selected(selection.counties, "counties"),
        selected(selection.cafv_statuses, "CAFV statuses"),
    )
    return " · ".join(parts)
