"""Shared cascading filter controls for analytical dashboard pages."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from electricvehicles.filtering import (
    FilterSelection,
    apply_filters,
    available_values,
)

FILTER_WIDGET_KEYS = (
    "filter_scope",
    "filter_years",
    "filter_ev_types",
    "filter_makes",
    "filter_counties",
    "filter_cafv",
)


def _reset_filters() -> None:
    """Remove only dashboard-owned filter state before Streamlit reruns."""
    for key in FILTER_WIDGET_KEYS:
        st.session_state.pop(key, None)


def _selection_for_options(
    selected: list[str], available: tuple[str, ...]
) -> tuple[str, ...]:
    """Discard stale cascading selections that no longer exist upstream."""
    allowed = set(available)
    return tuple(value for value in selected if value in allowed)


def render_global_filters(frame: pd.DataFrame) -> FilterSelection:
    """Render cascading controls and return their presentation-free state.

    Upstream choices constrain downstream option lists. Empty multiselects mean
    all available values and this convention is repeated in sidebar help text.
    """
    years = frame["model_year"].dropna()
    minimum_year, maximum_year = int(years.min()), int(years.max())

    with st.sidebar:
        st.header("Filters")
        st.caption("Empty selections include all available values.")
        scope = st.radio(
            "Location scope",
            ("Washington only", "All source states"),
            key="filter_scope",
            help=(
                "The source includes a small number of registered-owner addresses "
                "outside WA."
            ),
        )
        year_range = st.slider(
            "Model year",
            min_value=minimum_year,
            max_value=maximum_year,
            value=(minimum_year, maximum_year),
            key="filter_years",
        )

        upstream = FilterSelection(
            washington_only=scope == "Washington only",
            model_year_min=year_range[0],
            model_year_max=year_range[1],
        )
        scoped = apply_filters(frame, upstream)
        ev_options = available_values(scoped, "ev_type_code")
        ev_types = st.multiselect(
            "EV type",
            ev_options,
            key="filter_ev_types",
            help="BEV means battery electric; PHEV means plug-in hybrid.",
        )

        upstream = FilterSelection(
            washington_only=upstream.washington_only,
            model_year_min=upstream.model_year_min,
            model_year_max=upstream.model_year_max,
            ev_types=_selection_for_options(ev_types, ev_options),
        )
        scoped = apply_filters(frame, upstream)
        make_options = available_values(scoped, "make")
        makes = st.multiselect("Make", make_options, key="filter_makes")

        upstream = FilterSelection(
            washington_only=upstream.washington_only,
            model_year_min=upstream.model_year_min,
            model_year_max=upstream.model_year_max,
            ev_types=upstream.ev_types,
            makes=_selection_for_options(makes, make_options),
        )
        scoped = apply_filters(frame, upstream)
        county_options = available_values(scoped, "county")
        counties = st.multiselect("County", county_options, key="filter_counties")

        upstream = FilterSelection(
            washington_only=upstream.washington_only,
            model_year_min=upstream.model_year_min,
            model_year_max=upstream.model_year_max,
            ev_types=upstream.ev_types,
            makes=upstream.makes,
            counties=_selection_for_options(counties, county_options),
        )
        scoped = apply_filters(frame, upstream)
        cafv_options = available_values(scoped, "cafv_status")
        cafv = st.multiselect(
            "CAFV status",
            cafv_options,
            key="filter_cafv",
            help="Unknown remains a separate source category.",
        )
        st.button("Reset filters", on_click=_reset_filters, use_container_width=True)

    return FilterSelection(
        washington_only=upstream.washington_only,
        model_year_min=upstream.model_year_min,
        model_year_max=upstream.model_year_max,
        ev_types=upstream.ev_types,
        makes=upstream.makes,
        counties=upstream.counties,
        cafv_statuses=_selection_for_options(cafv, cafv_options),
    )
