"""Streamlit entry point and resilient application-shell composition.

This file deliberately stays thin: core data behavior is implemented in
Streamlit-independent modules, while this boundary owns caching, navigation,
sidebar controls, and safe user-facing failure states.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

import streamlit as st

from electricvehicles.application import (
    LoadedApplicationData,
    build_page_context,
    load_application_data,
)
from electricvehicles.config import get_data_path
from electricvehicles.ingestion import DataLoadError
from electricvehicles.pages import data_quality, geography, market, overview, range_cafv
from electricvehicles.quality import QualityBaselineError
from electricvehicles.ui.components import load_shared_styles
from electricvehicles.ui.sidebar import render_global_filters
from electricvehicles.validation import DataValidationError


@st.cache_data(show_spinner=False)
def _load_cached(
    path_text: str, file_size: int, modified_nanoseconds: int
) -> LoadedApplicationData:
    """Cache the full pipeline using source identity as invalidation metadata.

    ``file_size`` and ``modified_nanoseconds`` are intentionally unused inside
    the function body; their presence in the cache key invalidates stale data
    when a source file is replaced at the same path.
    """
    del file_size, modified_nanoseconds
    return load_application_data(path_text)


def _source_identity(path: Path) -> tuple[int, int]:
    """Return file metadata used to invalidate Streamlit's pipeline cache."""
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def _render_failure(title: str, message: str) -> None:
    """Show an actionable failure without exposing an internal traceback."""
    st.error(title)
    st.write(message)
    st.info("Review the local setup instructions in README.md and the Data Contract.")


def main() -> None:
    """Configure, load, filter, and run the five-page Streamlit application."""
    st.set_page_config(
        page_title="Electric Vehicles Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_shared_styles()

    source_path = get_data_path()
    try:
        file_size, modified = _source_identity(source_path)
        with st.spinner("Loading and validating vehicle data…", show_time=True):
            application = _load_cached(str(source_path), file_size, modified)
    except (DataLoadError, FileNotFoundError, OSError) as exc:
        _render_failure("Vehicle data could not be loaded.", str(exc))
        st.stop()
    except DataValidationError as exc:
        _render_failure("Vehicle data failed contract validation.", str(exc))
        st.stop()
    except QualityBaselineError as exc:
        _render_failure("The quality baseline could not be loaded.", str(exc))
        st.stop()

    filters = render_global_filters(application.clean_data)
    context = build_page_context(application, filters)

    pages = [
        st.Page(
            partial(overview.render, context),
            title="Overview",
            url_path="overview",
            default=True,
        ),
        st.Page(
            partial(market.render, context),
            title="Makes & Models",
            url_path="makes-models",
        ),
        st.Page(
            partial(geography.render, context),
            title="Geography",
            url_path="geography",
        ),
        st.Page(
            partial(range_cafv.render, context),
            title="Range & CAFV",
            url_path="range-cafv",
        ),
        st.Page(
            partial(data_quality.render, context),
            title="Data Quality",
            url_path="data-quality",
        ),
    ]
    st.navigation(pages, position="top").run()


if __name__ == "__main__":
    main()
