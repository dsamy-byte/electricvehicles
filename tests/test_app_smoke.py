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
