"""Tests for reusable Plotly encodings and accessible labels."""

from electricvehicles.analysis import CategoryResult
from electricvehicles.geography_data import GeographyRank, MapPoint
from electricvehicles.market_data import HeatmapCell, MarketRank
from electricvehicles.quality_page_data import MissingnessResult
from electricvehicles.range_cafv_data import RangeBin, RangeCoverage, RangeStatistics
from electricvehicles.ui.charts import (
    EV_TYPE_COLORS,
    aggregate_map_figure,
    concentration_figure,
    geography_ranking_figure,
    horizontal_category_figure,
    market_heatmap_figure,
    market_ranking_figure,
    missingness_figure,
    model_year_figure,
    range_coverage_figure,
    range_distribution_figure,
    range_interval_figure,
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
    assert EV_TYPE_COLORS == {"BEV": "#C2185B", "PHEV": "#B42318"}
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


def test_geography_ranking_retains_full_place_labels() -> None:
    results = (
        GeographyRank(1, "King, WA", "WA", "King", None, 80, 0.8),
        GeographyRank(2, "Clark, WA", "WA", "Clark", None, 20, 0.2),
    )

    figure = geography_ranking_figure(results)

    assert list(figure.data[0].y) == ["Clark, WA", "King, WA"]
    assert list(figure.data[0].customdata) == [0.2, 0.8]


def test_aggregate_map_contains_counts_without_identifiers() -> None:
    points = (MapPoint("WA", "King", "Seattle", -122.33, 47.61, 10),)

    figure = aggregate_map_figure(points)
    trace = figure.data[0]

    assert list(trace.lon) == [-122.33]
    assert list(trace.lat) == [47.61]
    assert list(trace.customdata[0]) == ["Seattle", "King", "WA", 10]
    assert "Vehicles" in trace.hovertemplate


def test_range_coverage_stacks_known_and_unknown_counts() -> None:
    coverage = (
        RangeCoverage("BEV", 10, 4, 6, 0.4),
        RangeCoverage("PHEV", 5, 5, 0, 1.0),
    )

    figure = range_coverage_figure(coverage)

    assert figure.layout.barmode == "stack"
    assert list(figure.data[0].x) == [4, 5]
    assert list(figure.data[1].x) == [6, 0]


def test_range_distribution_uses_preaggregated_bins() -> None:
    bins = (
        RangeBin("BEV", 100, 109, "100-109", 3),
        RangeBin("PHEV", 20, 29, "20-29", 4),
    )

    figure = range_distribution_figure(bins)

    assert len(figure.data) == 2
    assert list(figure.data[0].y) == [3]
    assert list(figure.data[1].y) == [4]


def test_range_interval_omits_types_without_known_values() -> None:
    statistics = (
        RangeStatistics("BEV", 10, 4, 0.4, 100, 150, 200, 190, 240, 300),
        RangeStatistics("PHEV", 5, 0, 0.0, None, None, None, None, None, None),
    )

    figure = range_interval_figure(statistics)

    assert len(figure.data) == 3
    assert list(figure.data[2].x) == [200]


def test_missingness_chart_retains_zero_missing_fields() -> None:
    """A complete field remains visible beside an incomplete field."""
    results = (
        MissingnessResult("optional", 5, 0.5, 5),
        MissingnessResult("complete", 0, 0.0, 10),
    )

    figure = missingness_figure(results)

    assert list(figure.data[0].y) == ["complete", "optional"]
    assert list(figure.data[0].x) == [0.0, 0.5]
    assert list(figure.data[0].customdata) == [0, 5]
