"""End-to-end Streamlit smoke test for the Geography renderer."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def _render_geography_fixture(source_path: str) -> None:
    """Build a real page context and render Geography for AppTest."""
    from electricvehicles.application import (
        build_page_context,
        load_application_data,
    )
    from electricvehicles.filtering import FilterSelection
    from electricvehicles.pages.geography import render

    application = load_application_data(source_path)
    selection = FilterSelection(
        washington_only=True,
        model_year_min=2020,
        model_year_max=2023,
    )
    render(build_page_context(application, selection))


def test_geography_page_renders_metrics_charts_and_tables() -> None:
    """Execute the real renderer and assert privacy-safe visible outputs."""
    app = AppTest.from_function(
        _render_geography_fixture,
        default_timeout=30,
        args=(str(FIXTURE.resolve()),),
    ).run()

    assert not app.exception
    assert [title.value for title in app.title] == ["Geography"]
    assert len(app.metric) == 4
    assert len(app.get("plotly_chart")) == 3
    assert len(app.expander) == 2
    assert len(app.dataframe) == 3
