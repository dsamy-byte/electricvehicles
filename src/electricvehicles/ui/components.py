"""Shared Streamlit components and shell-level visual behavior."""

from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from electricvehicles.application import PageContext
from electricvehicles.config import PROJECT_ROOT
from electricvehicles.filtering import describe_filters

STYLES_PATH = PROJECT_ROOT / "assets" / "styles.css"


def load_shared_styles(path: Path = STYLES_PATH) -> None:
    """Inject version-controlled local CSS without fetching remote assets."""
    styles = path.read_text(encoding="utf-8")
    st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)


def render_page_header(
    *, context: PageContext, eyebrow: str, title: str, description: str
) -> None:
    """Render a consistent analytical-page heading and active-filter context."""
    st.markdown(f'<p class="ev-eyebrow">{escape(eyebrow)}</p>', unsafe_allow_html=True)
    st.title(title)
    st.write(description)
    summary = escape(describe_filters(context.filters))
    st.markdown(f'<p class="ev-context">{summary}</p>', unsafe_allow_html=True)


def render_empty_state() -> None:
    """Render the documented no-match state without misleading zero charts."""
    st.info(
        "No vehicles match these filters. Change the sidebar selections or use "
        "Reset filters."
    )


def render_implementation_placeholder(next_task: str) -> None:
    """Mark a deliberately deferred page body during incremental delivery."""
    st.markdown(
        (
            '<div class="ev-placeholder"><strong>Page foundation ready.</strong><br>'
            f"The analytical content is scheduled for {escape(next_task)}.</div>"
        ),
        unsafe_allow_html=True,
    )
