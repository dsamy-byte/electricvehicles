"""Unfiltered data-quality page shell; content arrives in roadmap Task 13."""

import streamlit as st

from electricvehicles.application import PageContext
from electricvehicles.ui.components import render_implementation_placeholder


def render(context: PageContext) -> None:
    """Render unfiltered quality framing and baseline status."""
    st.markdown(
        '<p class="ev-eyebrow">Full source snapshot</p>', unsafe_allow_html=True
    )
    st.title("Data Quality")
    st.write(
        "Inspect provenance, validation, missingness, cleaning rules, and "
        "analytical limitations."
    )
    st.caption("Analytical sidebar filters do not affect this page.")
    quality = context.application.quality_report
    if quality.is_within_baseline:
        st.success("Baseline status: all configured checks passed.", icon="✓")
    else:
        st.warning("Baseline status: review required.", icon="⚠")
    render_implementation_placeholder("Task 13: Data quality and methodology")
