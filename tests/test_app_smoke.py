"""End-to-end Streamlit shell smoke test using the supported test runtime."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).parents[1] / "src" / "electricvehicles" / "app.py"
FIXTURE = Path(__file__).parent / "fixtures" / "valid_electric.csv"


def test_streamlit_shell_renders_without_exceptions(monkeypatch) -> None:
    """Execute the actual entry point, pipeline, sidebar, and default page."""
    monkeypatch.setenv("EV_DATA_PATH", str(FIXTURE.resolve()))

    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    assert not app.exception
    assert [title.value for title in app.title] == ["Electric Vehicles Overview"]
    assert app.sidebar.radio[0].value == "Washington only"
    assert app.sidebar.slider[0].value == (2020, 2023)


def test_ev_type_filter_updates_metrics_and_cascading_options(monkeypatch) -> None:
    """Exercise a real widget change, rerun, and downstream option refresh."""
    monkeypatch.setenv("EV_DATA_PATH", str(FIXTURE.resolve()))
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    app.sidebar.multiselect[0].select("BEV").run()

    assert not app.exception
    assert app.metric[0].label == "Vehicles"
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "100.0%"
    assert app.sidebar.multiselect[1].options == ["TESLA"]
    assert app.sidebar.multiselect[2].options == ["Yakima"]


def test_missing_source_shows_actionable_failure(monkeypatch, tmp_path) -> None:
    """Keep a missing local dataset user-facing and free of tracebacks."""
    missing_source = tmp_path / "missing-electric.csv"
    monkeypatch.setenv("EV_DATA_PATH", str(missing_source))

    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    assert not app.exception
    assert [error.value for error in app.error] == ["Vehicle data could not be loaded."]
    assert any("missing-electric.csv" in item.value for item in app.markdown)
    assert "README.md" in app.info[0].value


def test_empty_filter_result_shows_explanation_instead_of_charts(monkeypatch) -> None:
    """Verify the shell handles a valid filter combination with no rows."""
    monkeypatch.setenv("EV_DATA_PATH", str(FIXTURE.resolve()))
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    app.sidebar.slider[0].set_range(2021, 2022).run()

    assert not app.exception
    assert not app.metric
    assert not app.get("plotly_chart")
    assert any("No vehicles match" in item.value for item in app.info)
