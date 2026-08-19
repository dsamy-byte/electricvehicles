"""Overview page for the filtered current-registration population.

The renderer composes tested view-model calculations and reusable figures. It
contains no business aggregation logic, which keeps metric definitions stable
across Streamlit reruns and future consumers.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict

import pandas as pd
import streamlit as st

from electricvehicles.analysis import CategoryResult
from electricvehicles.application import PageContext
from electricvehicles.overview_data import OverviewData, build_overview_data
from electricvehicles.ui.charts import (
    EV_TYPE_COLORS,
    horizontal_category_figure,
    model_year_figure,
)
from electricvehicles.ui.components import (
    render_empty_state,
    render_page_header,
)


def _format_year(value: float) -> str:
    """Format an integral median year without an unnecessary decimal."""
    return str(int(value)) if value.is_integer() else f"{value:.1f}"


def _category_table(results: Sequence[CategoryResult]) -> pd.DataFrame:
    """Convert immutable category results into an accessible display table."""
    table = pd.DataFrame(asdict(result) for result in results)
    return table.rename(
        columns={"value": "Category", "count": "Vehicles", "share": "Share"}
    )


def _render_metrics(data: OverviewData) -> None:
    """Render five documented metrics with explicit denominator guidance."""
    columns = st.columns(5)
    columns[0].metric(
        "Vehicles",
        f"{data.vehicle_count:,}",
        help="Distinct DOL vehicle identifiers matching the active filters.",
    )
    columns[1].metric(
        "BEV share",
        f"{data.bev_share:.1%}",
        help=f"{data.bev_count:,} BEVs divided by all filtered vehicles.",
    )
    columns[2].metric(
        "Median model year",
        _format_year(data.median_model_year),
        help="Median model year in the filtered current population.",
    )
    columns[3].metric(
        "Known-range coverage",
        f"{data.known_range_share:.1%}",
        help=(
            f"{data.known_range_count:,} vehicles have researched, non-zero "
            "electric range. Unknown range is not treated as zero."
        ),
    )
    columns[4].metric(
        "CAFV eligible share",
        f"{data.eligible_share:.1%}",
        help=(
            f"{data.eligible_count:,} eligible vehicles divided by all filtered "
            "vehicles, including Unknown CAFV status."
        ),
    )


def _render_table(label: str, results: Sequence[CategoryResult]) -> None:
    """Provide exact chart values in an expandable keyboard-accessible table."""
    with st.expander(f"View {label} data"):
        st.dataframe(
            _category_table(results),
            hide_index=True,
            width="stretch",
            column_config={
                "Share": st.column_config.NumberColumn("Share", format="percent")
            },
        )


def render(context: PageContext) -> None:
    """Render headline metrics and three accessible population-composition views."""
    render_page_header(
        context=context,
        eyebrow="Current registration population",
        title="Electric Vehicles Overview",
        description=(
            "Explore the composition of electric vehicles currently registered "
            "through Washington State DOL."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return

    data = build_overview_data(context.filtered_data)
    _render_metrics(data)

    st.subheader("Model-year composition")
    st.caption(
        "Current population by vehicle model year—not annual sales or historical "
        "registration activity."
    )
    st.plotly_chart(
        model_year_figure(data.model_years),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    leading_year = max(data.model_years, key=lambda item: item.count)
    st.write(
        f"Model year {leading_year.value} is the largest group with "
        f"{leading_year.count:,} vehicles ({leading_year.share:.1%} of the "
        "filtered population)."
    )
    _render_table("model-year composition", data.model_years)

    left, right = st.columns(2)
    with left:
        st.subheader("Electric vehicle mix")
        st.caption("Battery electric (BEV) and plug-in hybrid (PHEV) vehicles.")
        st.plotly_chart(
            horizontal_category_figure(
                data.vehicle_types,
                colors=EV_TYPE_COLORS,
                height=270,
            ),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leader = data.vehicle_types[0]
        st.write(
            f"{leader.value} is the larger group with {leader.count:,} vehicles "
            f"({leader.share:.1%})."
        )
        _render_table("vehicle-type composition", data.vehicle_types)

    with right:
        st.subheader("Leading makes")
        st.caption("Top five manufacturers in the filtered current population.")
        st.plotly_chart(
            horizontal_category_figure(data.top_makes, height=270),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leading_make = data.top_makes[0]
        st.write(
            f"{leading_make.value.title()} leads with {leading_make.count:,} "
            f"vehicles ({leading_make.share:.1%})."
        )
        _render_table("leading-make composition", data.top_makes)

    st.info(
        "Read this correctly: this dashboard describes vehicles in a current "
        "registration snapshot. Model-year counts do not measure annual sales, "
        "annual registrations, or historical adoption."
    )
