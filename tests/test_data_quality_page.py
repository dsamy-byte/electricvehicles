"""End-to-end Streamlit smoke test for Data Quality and Methodology."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def _render_quality_fixture(source_path: str) -> None:
    """Build a filtered context and render unfiltered quality for AppTest."""
    from electricvehicles.application import (
        build_page_context,
        load_application_data,
    )
    from electricvehicles.filtering import FilterSelection
    from electricvehicles.pages.data_quality import render

    application = load_application_data(source_path)
    # This selection removes one fixture row. The page must still report two
    # full-source rows, proving that analytical filters are ignored.
    selection = FilterSelection(
        washington_only=True,
        model_year_min=2020,
        model_year_max=2020,
    )
    render(build_page_context(application, selection))


def test_quality_page_renders_unfiltered_metrics_chart_and_tables() -> None:
    """Execute the renderer and verify full-source quality outputs."""
    app = AppTest.from_function(
        _render_quality_fixture,
        default_timeout=30,
        args=(str(FIXTURE.resolve()),),
    ).run()

    assert not app.exception
    assert [title.value for title in app.title] == ["Data Quality"]
    assert len(app.metric) == 4
    assert app.metric[0].value == "2"
    assert len(app.get("plotly_chart")) == 1
    assert len(app.dataframe) == 3
    assert len(app.expander) == 3
