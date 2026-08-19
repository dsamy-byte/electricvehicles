"""Coverage-aware electric range and CAFV eligibility dashboard page.

This renderer never treats unknown range as zero and never combines unknown CAFV
status with eligible or not eligible. Tested view models own all calculations;
the page composes metrics, figures, narratives, and accessible tables.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict

import pandas as pd
import streamlit as st

from electricvehicles.analysis import CategoryResult
from electricvehicles.application import PageContext
from electricvehicles.range_cafv_data import (
    RangeBin,
    RangeCoverage,
    RangeStatistics,
    build_range_cafv_data,
)
from electricvehicles.ui.charts import (
    CAFV_COLORS,
    horizontal_category_figure,
    range_coverage_figure,
    range_distribution_figure,
    range_interval_figure,
)
from electricvehicles.ui.components import (
    render_empty_state,
    render_page_header,
)


def _format_miles(value: float | None) -> str:
    """Format a mileage metric or an accessible em dash when unavailable."""
    if value is None:
        return "—"
    return f"{value:,.0f} mi"


def _coverage_table(results: Sequence[RangeCoverage]) -> pd.DataFrame:
    """Return exact known/unknown coverage counts and rates by EV type."""
    return pd.DataFrame(
        {
            "EV type": [item.ev_type_code for item in results],
            "Vehicles": [item.vehicle_count for item in results],
            "Known range": [item.known_count for item in results],
            "Unknown range": [item.unknown_count for item in results],
            "Known coverage": [item.known_share for item in results],
        }
    )


def _statistics_table(results: Sequence[RangeStatistics]) -> pd.DataFrame:
    """Return per-type known-range coverage and five-number summaries."""
    return pd.DataFrame(asdict(item) for item in results).rename(
        columns={
            "ev_type_code": "EV type",
            "vehicle_count": "Vehicles",
            "known_count": "Known range",
            "known_share": "Known coverage",
            "minimum_miles": "Minimum",
            "percentile_25_miles": "25th percentile",
            "median_miles": "Median",
            "mean_miles": "Mean",
            "percentile_75_miles": "75th percentile",
            "maximum_miles": "Maximum",
        }
    )


def _bins_table(results: Sequence[RangeBin]) -> pd.DataFrame:
    """Return exact aggregated histogram bins without vehicle-level values."""
    return pd.DataFrame(
        {
            "EV type": [item.ev_type_code for item in results],
            "Range bin (miles)": [item.label for item in results],
            "Vehicles": [item.count for item in results],
        }
    )


def _cafv_table(results: Sequence[CategoryResult]) -> pd.DataFrame:
    """Return all populated CAFV categories, counts, and full-population shares."""
    return pd.DataFrame(
        {
            "CAFV status": [item.value for item in results],
            "Vehicles": [item.count for item in results],
            "Share": [item.share for item in results],
        }
    )


def render(context: PageContext) -> None:
    """Render coverage, distributions, per-type intervals, and CAFV composition."""
    render_page_header(
        context=context,
        eyebrow="Availability and eligibility",
        title="Range & CAFV",
        description=(
            "Interpret known electric range and all CAFV source categories responsibly."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return

    data = build_range_cafv_data(context.filtered_data)
    metrics = st.columns(4)
    metrics[0].metric(
        "Known-range coverage",
        f"{data.known_range_share:.1%}",
        help=(
            f"{data.known_range_count:,} vehicles have researched, non-zero "
            "electric range."
        ),
    )
    metrics[1].metric(
        "Median known range",
        _format_miles(data.median_known_range),
        help="Median among known values only; unknown records are excluded.",
    )
    metrics[2].metric(
        "CAFV eligible share",
        f"{data.eligible_share:.1%}",
        help=(
            f"{data.eligible_count:,} eligible vehicles divided by all filtered "
            "vehicles, including Unknown status."
        ),
    )
    metrics[3].metric(
        "CAFV unknown share",
        f"{data.unknown_cafv_share:.1%}",
        help=f"{data.unknown_cafv_count:,} vehicles have Unknown CAFV status.",
    )

    st.subheader("Range availability by vehicle type")
    st.caption(
        "Known and unknown counts are shown together so coverage differences are "
        "not hidden. Zero source range is classified as unknown."
    )
    st.plotly_chart(
        range_coverage_figure(data.coverage_by_type),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    with st.expander("View range coverage data"):
        st.dataframe(
            _coverage_table(data.coverage_by_type),
            hide_index=True,
            width="stretch",
            column_config={
                "Known coverage": st.column_config.NumberColumn(format="percent")
            },
        )

    st.subheader("Known electric-range distributions")
    st.caption(
        f"BEV and PHEV appear separately in {data.bin_width_miles}-mile bins. "
        "These distributions describe researched values only."
    )
    if data.range_bins:
        st.plotly_chart(
            range_distribution_figure(data.range_bins),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
    else:
        st.info("No researched electric-range values match the active filters.")
    with st.expander("View distribution-bin data"):
        st.dataframe(_bins_table(data.range_bins), hide_index=True, width="stretch")

    st.subheader("Known-range interval summary")
    st.caption(
        "Thin line: minimum-maximum. Thick line: 25th-75th percentile. Diamond: median."
    )
    if any(item.known_count for item in data.statistics_by_type):
        st.plotly_chart(
            range_interval_figure(data.statistics_by_type),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
    with st.expander("View known-range statistics"):
        st.dataframe(
            _statistics_table(data.statistics_by_type),
            hide_index=True,
            width="stretch",
            column_config={
                "Known coverage": st.column_config.NumberColumn(format="percent")
            },
        )

    st.subheader("CAFV eligibility")
    st.caption(
        "Unknown remains a separate source category and is included in headline "
        "share denominators."
    )
    st.plotly_chart(
        horizontal_category_figure(
            data.cafv_statuses,
            colors=CAFV_COLORS,
            height=300,
        ),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    with st.expander("View CAFV status data"):
        st.dataframe(
            _cafv_table(data.cafv_statuses),
            hide_index=True,
            width="stretch",
            column_config={"Share": st.column_config.NumberColumn(format="percent")},
        )

    st.warning(
        "Selection-bias warning: known range covers a much smaller share of BEVs "
        "than PHEVs in this source. Known-value statistics do not characterize "
        "vehicles whose range has not been researched."
    )
