"""Accessible, consistently styled Plotly figures for dashboard pages.

Figure builders accept already-aggregated data and do not import Streamlit.
This allows visual encodings, labels, ordering, and hover content to be tested
without starting the application. Every chart is paired with narrative text and
an accessible value table by its page renderer; Plotly hover is never the only
way to retrieve a value.
"""

from __future__ import annotations

from collections.abc import Sequence

import plotly.graph_objects as go

from electricvehicles.analysis import CategoryResult
from electricvehicles.market_data import HeatmapCell, MarketRank

ELECTRIC_BLUE = "#1769AA"
TEAL = "#147D78"
INK = "#14213D"
MUTED_INK = "#52606D"
BORDER = "#D9E2EC"
SURFACE = "#FFFFFF"
EV_TYPE_COLORS = {"BEV": ELECTRIC_BLUE, "PHEV": TEAL}


def _base_layout(figure: go.Figure, *, height: int) -> go.Figure:
    """Apply the shared low-decoration, readable dashboard chart treatment."""
    figure.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=24, b=16),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(color=INK, size=14),
        hoverlabel=dict(bgcolor=SURFACE, font_color=INK),
        showlegend=False,
    )
    figure.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED_INK),
        title_font=dict(color=MUTED_INK),
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor=BORDER,
        zeroline=False,
        tickfont=dict(color=MUTED_INK),
        title_font=dict(color=MUTED_INK),
    )
    return figure


def model_year_figure(results: Sequence[CategoryResult]) -> go.Figure:
    """Build a chronological column chart of current population by model year.

    Args:
        results: Chronologically ordered model-year counts and shares.

    Returns:
        Plotly figure with integer year labels, count axis, and count/share hover
        values. The page supplies the non-historical interpretation subtitle.
    """
    years = [result.value for result in results]
    counts = [result.count for result in results]
    shares = [result.share for result in results]
    figure = go.Figure(
        go.Bar(
            x=years,
            y=counts,
            marker_color=ELECTRIC_BLUE,
            customdata=shares,
            hovertemplate=(
                "Model year %{x}<br>Vehicles %{y:,}<br>Share %{customdata:.1%}"
                "<extra></extra>"
            ),
        )
    )
    _base_layout(figure, height=390)
    figure.update_xaxes(title_text="Model year", type="category")
    figure.update_yaxes(title_text="Vehicles", tickformat=",")
    return figure


def horizontal_category_figure(
    results: Sequence[CategoryResult],
    *,
    x_title: str = "Vehicles",
    colors: dict[str, str] | None = None,
    height: int = 310,
) -> go.Figure:
    """Build a ranked horizontal bar chart with readable category labels.

    Results arrive in descending rank order and are reversed for Plotly so the
    leading category appears at the top. Optional semantic colors are keyed by
    exact category value; unmatched categories use Electric Blue.
    """
    ordered = list(reversed(results))
    labels = [result.value for result in ordered]
    counts = [result.count for result in ordered]
    shares = [result.share for result in ordered]
    palette = colors or {}
    bar_colors = [palette.get(label, ELECTRIC_BLUE) for label in labels]
    figure = go.Figure(
        go.Bar(
            x=counts,
            y=labels,
            orientation="h",
            marker_color=bar_colors,
            customdata=shares,
            text=[f"{count:,}" for count in counts],
            textposition="auto",
            hovertemplate=(
                "%{y}<br>Vehicles %{x:,}<br>Share %{customdata:.1%}<extra></extra>"
            ),
        )
    )
    _base_layout(figure, height=height)
    figure.update_xaxes(title_text=x_title, tickformat=",")
    figure.update_yaxes(title_text=None)
    return figure


def market_ranking_figure(
    results: Sequence[MarketRank], *, height: int | None = None
) -> go.Figure:
    """Build a horizontal count/share chart for ranked market records.

    Chart height grows with the selected Top N count while remaining bounded so
    labels stay readable without dominating the page.
    """
    ordered = list(reversed(results))
    labels = [result.label for result in ordered]
    counts = [result.count for result in ordered]
    shares = [result.share for result in ordered]
    figure = go.Figure(
        go.Bar(
            x=counts,
            y=labels,
            orientation="h",
            marker_color=ELECTRIC_BLUE,
            customdata=shares,
            hovertemplate=(
                "%{y}<br>Vehicles %{x:,}<br>Share %{customdata:.1%}<extra></extra>"
            ),
        )
    )
    chart_height = height or max(300, min(700, 44 * len(results) + 100))
    _base_layout(figure, height=chart_height)
    figure.update_xaxes(title_text="Vehicles", tickformat=",")
    figure.update_yaxes(title_text=None)
    return figure


def concentration_figure(results: Sequence[MarketRank]) -> go.Figure:
    """Build cumulative make concentration by rank with reference thresholds."""
    ranks = [result.rank for result in results]
    cumulative = [result.cumulative_share for result in results]
    figure = go.Figure(
        go.Scatter(
            x=ranks,
            y=cumulative,
            mode="lines+markers",
            line=dict(color=TEAL, width=3),
            marker=dict(color=TEAL, size=6),
            customdata=[result.label for result in results],
            hovertemplate=(
                "Rank %{x}: %{customdata}<br>Cumulative share %{y:.1%}<extra></extra>"
            ),
        )
    )
    for threshold in (0.5, 0.75, 0.9):
        figure.add_hline(
            y=threshold,
            line_dash="dot",
            line_color=BORDER,
            annotation_text=f"{threshold:.0%}",
            annotation_position="right",
        )
    _base_layout(figure, height=360)
    figure.update_xaxes(title_text="Make rank", dtick=5)
    figure.update_yaxes(title_text="Cumulative population share", tickformat=".0%")
    return figure


def market_heatmap_figure(
    cells: Sequence[HeatmapCell],
    makes: Sequence[str],
    model_years: Sequence[int],
) -> go.Figure:
    """Build a make-by-model-year count heatmap from a complete cell grid."""
    lookup = {(cell.make, cell.model_year): cell.count for cell in cells}
    values = [[lookup.get((make, year), 0) for year in model_years] for make in makes]
    figure = go.Figure(
        go.Heatmap(
            x=[str(year) for year in model_years],
            y=list(makes),
            z=values,
            colorscale=[[0, "#EEF5FB"], [1, ELECTRIC_BLUE]],
            colorbar=dict(title="Vehicles", tickformat=","),
            hovertemplate=("%{y}<br>Model year %{x}<br>Vehicles %{z:,}<extra></extra>"),
        )
    )
    _base_layout(figure, height=max(390, min(620, 42 * len(makes) + 190)))
    figure.update_xaxes(title_text="Model year", type="category")
    figure.update_yaxes(title_text="Make", showgrid=False, autorange="reversed")
    return figure
