"""Tests for reusable Plotly encodings and accessible labels."""

from electricvehicles.analysis import CategoryResult
from electricvehicles.market_data import HeatmapCell, MarketRank
from electricvehicles.ui.charts import (
    EV_TYPE_COLORS,
    concentration_figure,
    horizontal_category_figure,
    market_heatmap_figure,
    market_ranking_figure,
    model_year_figure,
)


def test_model_year_chart_preserves_chronology_and_context() -> None:
    results = (
        CategoryResult("2020", 10, 0.4),
        CategoryResult("2021", 15, 0.6),
    )

    figure = model_year_figure(results)
    trace = figure.data[0]

    assert list(trace.x) == ["2020", "2021"]
    assert list(trace.y) == [10, 15]
    assert "Share" in trace.hovertemplate
    assert figure.layout.xaxis.title.text == "Model year"
    assert figure.layout.yaxis.title.text == "Vehicles"


def test_horizontal_chart_puts_leading_category_at_top() -> None:
    results = (
        CategoryResult("BEV", 80, 0.8),
        CategoryResult("PHEV", 20, 0.2),
    )

    figure = horizontal_category_figure(results, colors=EV_TYPE_COLORS)
    trace = figure.data[0]

    # Plotly renders the final horizontal category at the top, so ranked input
    # is reversed while preserving the visual leader-first result.
    assert list(trace.y) == ["PHEV", "BEV"]
    assert list(trace.marker.color) == [EV_TYPE_COLORS["PHEV"], EV_TYPE_COLORS["BEV"]]
    assert list(trace.customdata) == [0.2, 0.8]


def test_market_ranking_and_concentration_use_ranked_values() -> None:
    results = (
        MarketRank(1, "TESLA", "TESLA", None, 80, 0.8, 0.8),
        MarketRank(2, "FORD", "FORD", None, 20, 0.2, 1.0),
    )

    ranking = market_ranking_figure(results)
    concentration = concentration_figure(results)

    assert list(ranking.data[0].y) == ["FORD", "TESLA"]
    assert list(concentration.data[0].x) == [1, 2]
    assert list(concentration.data[0].y) == [0.8, 1.0]


def test_market_heatmap_uses_complete_grid() -> None:
    cells = (
        HeatmapCell("TESLA", 2020, 2),
        HeatmapCell("TESLA", 2021, 3),
        HeatmapCell("FORD", 2020, 1),
        HeatmapCell("FORD", 2021, 0),
    )

    figure = market_heatmap_figure(cells, ("TESLA", "FORD"), (2020, 2021))

    assert list(figure.data[0].x) == ["2020", "2021"]
    assert list(figure.data[0].y) == ["TESLA", "FORD"]
    assert [list(row) for row in figure.data[0].z] == [[2, 3], [1, 0]]
