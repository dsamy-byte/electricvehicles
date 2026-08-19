"""Static regression tests for accessibility and privacy design contracts.

These checks complement interactive Streamlit tests. They protect critical
requirements that are easy to accidentally remove during visual refactoring,
but do not claim to replace manual keyboard and screen-reader verification.
"""

from pathlib import Path

from electricvehicles.geography_data import MapPoint

PROJECT_ROOT = Path(__file__).parents[1]


def test_shared_styles_preserve_visible_keyboard_focus() -> None:
    """Require a strong focus-visible rule in the shared stylesheet."""
    styles = (PROJECT_ROOT / "assets" / "styles.css").read_text(encoding="utf-8")

    assert ":focus-visible" in styles
    assert "outline:" in styles
    assert "outline-offset:" in styles


def test_pages_offer_exact_tables_for_every_chart() -> None:
    """Require the reusable exact-data table pattern on analytical pages."""
    page_directory = PROJECT_ROOT / "src" / "electricvehicles" / "pages"
    for filename in ("overview.py", "market.py", "geography.py", "range_cafv.py"):
        source = (page_directory / filename).read_text(encoding="utf-8")
        assert "st.plotly_chart(" in source
        assert "st.dataframe(" in source
        assert "st.expander(" in source


def test_geography_never_sends_vehicle_identifier_to_map_model() -> None:
    """Prevent vehicle-level identifiers from entering aggregate map output."""
    assert "dol_vehicle_id" not in MapPoint.__dataclass_fields__
