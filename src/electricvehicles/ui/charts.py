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
from plotly.subplots import make_subplots

from electricvehicles.analysis import CategoryResult
from electricvehicles.geography_data import GeographyRank, MapPoint
from electricvehicles.market_data import HeatmapCell, MarketRank
from electricvehicles.quality_page_data import MissingnessResult
from electricvehicles.range_cafv_data import RangeBin, RangeCoverage, RangeStatistics

ELECTRIC_BLUE = "#1769AA"
TEAL = "#147D78"
INK = "#14213D"
MUTED_INK = "#52606D"
BORDER = "#D9E2EC"
SURFACE = "#FFFFFF"
EV_TYPE_COLORS = {"BEV": ELECTRIC_BLUE, "PHEV": TEAL}
CAFV_COLORS = {
    "Eligible": "#287D3C",
    "Not eligible": "#B42318",
    "Unknown": "#B26A00",
}


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


def geography_ranking_figure(
    results: Sequence[GeographyRank], *, height: int | None = None
) -> go.Figure:
    """Build a readable horizontal county/city ranking chart."""
    ordered = list(reversed(results))
    figure = go.Figure(
        go.Bar(
            x=[result.count for result in ordered],
            y=[result.label for result in ordered],
            orientation="h",
            marker_color=ELECTRIC_BLUE,
            customdata=[result.share for result in ordered],
            hovertemplate=(
                "%{y}<br>Vehicles %{x:,}<br>Share %{customdata:.1%}<extra></extra>"
            ),
        )
    )
    chart_height = height or max(320, min(720, 44 * len(results) + 100))
    _base_layout(figure, height=chart_height)
    figure.update_xaxes(title_text="Vehicles", tickformat=",")
    figure.update_yaxes(title_text=None)
    return figure


def aggregate_map_figure(points: Sequence[MapPoint]) -> go.Figure:
    """Build a token-free map containing aggregate place counts only.

    Marker areas scale with the square root of count so the largest population
    centers do not visually erase smaller places. Tooltips contain aggregate
    place names and counts; no source identifiers or vehicle rows are present.
    """
    maximum = max((point.count for point in points), default=1)
    marker_sizes = [7 + 31 * (point.count / maximum) ** 0.5 for point in points]
    figure = go.Figure(
        go.Scattermap(
            lon=[point.longitude for point in points],
            lat=[point.latitude for point in points],
            mode="markers",
            marker=dict(
                size=marker_sizes,
                color=ELECTRIC_BLUE,
                opacity=0.68,
            ),
            customdata=[
                (point.city, point.county, point.state, point.count) for point in points
            ],
            hovertemplate=(
                "%{customdata[0]}, %{customdata[2]}<br>"
                "%{customdata[1]} County<br>"
                "Vehicles %{customdata[3]:,}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=SURFACE,
        font=dict(color=INK, size=14),
        map=dict(style="carto-positron", center=dict(lat=47.4, lon=-120.7), zoom=5),
        showlegend=False,
    )
    return figure


def range_coverage_figure(results: Sequence[RangeCoverage]) -> go.Figure:
    """Build a stacked known/unknown coverage chart for each EV type."""
    labels = [result.ev_type_code for result in results]
    known = [result.known_count for result in results]
    unknown = [result.unknown_count for result in results]
    figure = go.Figure()
    figure.add_bar(
        name="Known range",
        y=labels,
        x=known,
        orientation="h",
        marker_color=TEAL,
        hovertemplate="%{y}<br>Known %{x:,}<extra></extra>",
    )
    figure.add_bar(
        name="Unknown range",
        y=labels,
        x=unknown,
        orientation="h",
        marker_color="#B26A00",
        hovertemplate="%{y}<br>Unknown %{x:,}<extra></extra>",
    )
    _base_layout(figure, height=290)
    figure.update_layout(barmode="stack", showlegend=True, legend_title_text=None)
    figure.update_xaxes(title_text="Vehicles", tickformat=",")
    figure.update_yaxes(title_text=None, showgrid=False)
    return figure


def range_distribution_figure(results: Sequence[RangeBin]) -> go.Figure:
    """Build separate known-range histograms from pre-aggregated bins."""
    ev_types = sorted({result.ev_type_code for result in results})
    if not ev_types:
        return _base_layout(go.Figure(), height=300)
    figure = make_subplots(
        rows=len(ev_types),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.13,
        subplot_titles=[f"{ev_type} — known values" for ev_type in ev_types],
    )
    for row, ev_type in enumerate(ev_types, start=1):
        values = [item for item in results if item.ev_type_code == ev_type]
        figure.add_trace(
            go.Bar(
                x=[item.lower_miles for item in values],
                y=[item.count for item in values],
                width=[item.upper_miles - item.lower_miles + 1 for item in values],
                marker_color=EV_TYPE_COLORS.get(ev_type, ELECTRIC_BLUE),
                customdata=[item.label for item in values],
                hovertemplate=("%{customdata} miles<br>Vehicles %{y:,}<extra></extra>"),
                showlegend=False,
            ),
            row=row,
            col=1,
        )
    _base_layout(figure, height=max(330, 270 * len(ev_types)))
    figure.update_xaxes(title_text="Known electric range (miles)", row=len(ev_types))
    figure.update_yaxes(title_text="Vehicles", tickformat=",")
    return figure


def range_interval_figure(results: Sequence[RangeStatistics]) -> go.Figure:
    """Show min/max, interquartile range, and median for known values only."""
    available = [result for result in results if result.median_miles is not None]
    figure = go.Figure()
    for result in available:
        color = EV_TYPE_COLORS.get(result.ev_type_code, ELECTRIC_BLUE)
        figure.add_trace(
            go.Scatter(
                x=[result.minimum_miles, result.maximum_miles],
                y=[result.ev_type_code, result.ev_type_code],
                mode="lines",
                line=dict(color=BORDER, width=4),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        figure.add_trace(
            go.Scatter(
                x=[result.percentile_25_miles, result.percentile_75_miles],
                y=[result.ev_type_code, result.ev_type_code],
                mode="lines",
                line=dict(color=color, width=16),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        figure.add_trace(
            go.Scatter(
                x=[result.median_miles],
                y=[result.ev_type_code],
                mode="markers",
                marker=dict(color=INK, size=11, symbol="diamond"),
                customdata=[(result.known_count, result.known_share)],
                hovertemplate=(
                    "%{y}<br>Median %{x:.1f} miles<br>Known %{customdata[0]:,} "
                    "(%{customdata[1]:.1%})<extra></extra>"
                ),
                showlegend=False,
            )
        )
    _base_layout(figure, height=max(280, 100 * len(available) + 140))
    figure.update_xaxes(title_text="Known electric range (miles)")
    figure.update_yaxes(title_text=None, showgrid=False)
    return figure


def missingness_figure(results: Sequence[MissingnessResult]) -> go.Figure:
    """Build a missing-rate chart that retains fully populated fields.

    Including zero-missing fields lets users distinguish measured completeness
    from fields omitted from reporting. Amber plus exact hover text identifies
    incomplete fields without relying on color alone.
    """
    ordered = list(reversed(results))
    figure = go.Figure(
        go.Bar(
            x=[result.missing_rate for result in ordered],
            y=[result.column for result in ordered],
            orientation="h",
            marker_color=[
                "#B26A00" if result.missing_count else TEAL for result in ordered
            ],
            customdata=[result.missing_count for result in ordered],
            hovertemplate=(
                "%{y}<br>Missing %{customdata:,}<br>Rate %{x:.2%}<extra></extra>"
            ),
        )
    )
    _base_layout(figure, height=max(520, 30 * len(results) + 120))
    figure.update_xaxes(title_text="Missing share", tickformat=".0%")
    figure.update_yaxes(title_text=None, showgrid=False)
    return figure
