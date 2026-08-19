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
