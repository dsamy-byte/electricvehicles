"""Makes & Models page for rankings and manufacturer concentration.

All aggregations come from ``market_data.py``. This renderer owns only local
display controls, narrative composition, figures, and accessible value tables.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import streamlit as st

from electricvehicles.application import PageContext
from electricvehicles.market_data import HeatmapCell, MarketRank, build_market_data
from electricvehicles.ui.charts import (
    concentration_figure,
    market_heatmap_figure,
    market_ranking_figure,
)
from electricvehicles.ui.components import (
    render_empty_state,
    render_page_header,
)

TOP_N_OPTIONS = (5, 10, 20)


def _ranking_table(results: Sequence[MarketRank]) -> pd.DataFrame:
    """Build an accessible table with exact rank, count, and share values."""
    return pd.DataFrame(
        {
            "Rank": [result.rank for result in results],
            "Category": [result.label for result in results],
            "Vehicles": [result.count for result in results],
            "Share": [result.share for result in results],
            "Cumulative share": [result.cumulative_share for result in results],
        }
    )


def _render_ranking_table(label: str, results: Sequence[MarketRank]) -> None:
    """Render exact ranking values as an expandable keyboard-accessible table."""
    with st.expander(f"View {label} data"):
        st.dataframe(
            _ranking_table(results),
            hide_index=True,
            width="stretch",
            column_config={
                "Share": st.column_config.NumberColumn(format="percent"),
                "Cumulative share": st.column_config.NumberColumn(format="percent"),
            },
        )


def _heatmap_table(cells: Sequence[HeatmapCell]) -> pd.DataFrame:
    """Return long-form heatmap values for accessible inspection and download."""
    return pd.DataFrame(
        {
            "Make": [cell.make for cell in cells],
            "Model year": [cell.model_year for cell in cells],
            "Vehicles": [cell.count for cell in cells],
        }
    )


def render(context: PageContext) -> None:
    """Render market metrics, rankings, concentration, and composition heatmap."""
    render_page_header(
        context=context,
        eyebrow="Market composition",
        title="Makes & Models",
        description=(
            "Compare manufacturer and model concentration in the selected population."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return

    market = build_market_data(context.filtered_data, heatmap_make_limit=10)
    metrics = st.columns(4)
    metrics[0].metric(
        "Distinct makes",
        f"{market.make_count:,}",
        help="Populated manufacturer labels in the filtered population.",
    )
    metrics[1].metric(
        "Make/model combinations",
        f"{market.make_model_count:,}",
        help="Distinct (make, model) pairs; model labels are not merged across makes.",
    )
    metrics[2].metric(
        "Leading make",
        market.leading_make.title(),
        help=(
            f"{market.leading_make_count:,} vehicles, or "
            f"{market.leading_make_share:.1%} of the filtered population."
        ),
    )
    metrics[3].metric(
        "Top-10 make share",
        f"{market.top_10_make_share:.1%}",
        help="Combined share of up to ten leading makes after active filters.",
    )

    makes_tab, models_tab = st.tabs(("Makes", "Models"))
    with makes_tab:
        make_limit = st.segmented_control(
            "Number of makes",
            TOP_N_OPTIONS,
            default=10,
            key="market_make_limit",
        )
        visible_makes = market.make_rankings[: int(make_limit or 10)]
        st.plotly_chart(
            market_ranking_figure(visible_makes),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leader = visible_makes[0]
        st.write(
            f"{leader.make.title()} ranks first with {leader.count:,} vehicles "
            f"({leader.share:.1%} of the filtered population)."
        )
        _render_ranking_table("make ranking", visible_makes)

    with models_tab:
        model_limit = st.segmented_control(
            "Number of models",
            TOP_N_OPTIONS,
            default=10,
            key="market_model_limit",
        )
        visible_models = market.model_rankings[: int(model_limit or 10)]
        st.plotly_chart(
            market_ranking_figure(visible_models),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leader = visible_models[0]
        st.write(
            f"{leader.model.title()} by {leader.make.title()} ranks first with "
            f"{leader.count:,} vehicles ({leader.share:.1%})."
        )
        _render_ranking_table("model ranking", visible_models)

    st.subheader("Cumulative make concentration")
    st.caption(
        "How quickly the filtered population is accounted for as makes are added "
        "from largest to smallest."
    )
    st.plotly_chart(
        concentration_figure(market.make_rankings),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    st.write(
        f"The ten leading makes account for {market.top_10_make_share:.1%} of "
        "the filtered population."
    )
    _render_ranking_table("complete make concentration", market.make_rankings)

    st.subheader("Leading makes by model year")
    st.caption(
        "Current-population counts by vehicle model year—not annual sales or "
        "registration history."
    )
    st.plotly_chart(
        market_heatmap_figure(
            market.heatmap_cells,
            market.heatmap_makes,
            market.model_years,
        ),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    with st.expander("View heatmap data"):
        st.dataframe(
            _heatmap_table(market.heatmap_cells),
            hide_index=True,
            width="stretch",
        )

    st.info(
        "Market shares describe this filtered current-registration population. "
        "They are not sales shares, and model-year patterns are not a historical "
        "adoption series."
    )
