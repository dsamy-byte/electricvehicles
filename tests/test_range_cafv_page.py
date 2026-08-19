"""End-to-end Streamlit smoke test for the Range & CAFV renderer."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def _render_range_fixture(source_path: str) -> None:
    """Build a real page context and render Range & CAFV for AppTest."""
    from electricvehicles.application import (
        build_page_context,
        load_application_data,
    )
    from electricvehicles.filtering import FilterSelection
    from electricvehicles.pages.range_cafv import render

    application = load_application_data(source_path)
    selection = FilterSelection(
        washington_only=True,
        model_year_min=2020,
        model_year_max=2023,
    )
    render(build_page_context(application, selection))


def test_range_page_renders_metrics_charts_and_tables() -> None:
    """Execute the real renderer and assert its coverage-aware outputs."""
    app = AppTest.from_function(
        _render_range_fixture,
        default_timeout=30,
        args=(str(FIXTURE.resolve()),),
    ).run()

    assert not app.exception
    assert [title.value for title in app.title] == ["Range & CAFV"]
    assert len(app.metric) == 4
    # The fixture has known BEV range, so all four specified figures render.
    assert len(app.get("plotly_chart")) == 4
    assert len(app.expander) == 4
    assert len(app.dataframe) == 4
