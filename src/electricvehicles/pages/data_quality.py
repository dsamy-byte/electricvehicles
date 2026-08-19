"""Unfiltered Data Quality and Methodology dashboard page.

Unlike analytical pages, this renderer uses only full-source application
artifacts. Sidebar filters never alter provenance, validation, baseline,
missingness, or dictionary content.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict

import pandas as pd
import streamlit as st

from electricvehicles.application import PageContext
from electricvehicles.data_contract import FieldDefinition
from electricvehicles.quality_page_data import (
    BaselineResult,
    MissingnessResult,
    build_quality_page_data,
)
from electricvehicles.ui.charts import missingness_figure


def _baseline_table(results: Sequence[BaselineResult]) -> pd.DataFrame:
    """Return every baseline observation and its explicit expectation."""
    return pd.DataFrame(asdict(result) for result in results).rename(
        columns={
            "metric": "Metric",
            "observed": "Observed",
            "expectation": "Expectation",
            "status": "Status",
        }
    )


def _missingness_table(results: Sequence[MissingnessResult]) -> pd.DataFrame:
    """Return exact completeness counts and rates for all clean fields."""
    return pd.DataFrame(asdict(result) for result in results).rename(
        columns={
            "column": "Column",
            "missing_count": "Missing",
            "missing_rate": "Missing rate",
            "populated_count": "Populated",
        }
    )


def _dictionary_table(definitions: Sequence[FieldDefinition]) -> pd.DataFrame:
    """Return the executable 22-field clean data dictionary."""
    return pd.DataFrame(asdict(item) for item in definitions).rename(
        columns={
            "clean_name": "Clean field",
            "source_name": "Source",
            "logical_type": "Logical type",
            "nullable": "Nullable",
            "description": "Definition",
        }
    )


def render(context: PageContext) -> None:
    """Render full-source provenance, quality, dictionary, and methodology."""
    data = build_quality_page_data(context.application)
    st.markdown(
        '<p class="ev-eyebrow">Full source snapshot</p>', unsafe_allow_html=True
    )
    st.title("Data Quality")
    st.write(
        "Inspect provenance, validation, missingness, cleaning rules, and "
        "analytical limitations."
    )
    st.caption("Analytical sidebar filters do not affect this page.")

    metrics = st.columns(4)
    metrics[0].metric("Source rows", f"{data.row_count:,}")
    metrics[1].metric("Clean fields", f"{data.column_count:,}")
    metrics[2].metric("Validation warnings", f"{data.warning_count:,}")
    metrics[3].metric(
        "Baseline checks",
        f"{data.baseline_passed_count}/{data.baseline_check_count} passed",
    )
    if data.baseline_passed:
        st.success("Baseline status: all configured checks passed.")
    else:
        st.warning("Baseline status: review required.")

    st.subheader("Provenance")
    st.markdown(
        f"**Dataset:** [{data.dataset_name}]({data.dataset_url})  \n"
        f"**Publisher:** {data.publisher}  \n"
        f"**Dataset ID:** `{data.dataset_id}`  \n"
        f"**Data license:** [{data.license_name}]({data.license_url})  \n"
        f"**Local source file:** `{data.source_file_name}`  \n"
        f"**File size:** {data.source_size_bytes:,} bytes  \n"
        f"**SHA-256:** `{data.source_sha256}`"
    )
    st.caption(
        "The fingerprint identifies the loaded local snapshot. Publisher data may "
        "change when Data.WA refreshes the registration population."
    )

    st.subheader("Validation and baseline checks")
    st.dataframe(
        _baseline_table(data.baseline_results),
        hide_index=True,
        width="stretch",
    )
    with st.expander("View validation warnings"):
        if data.validation_warnings:
            for warning in data.validation_warnings:
                st.write(f"- {warning}")
        else:
            st.write("No non-blocking validation warnings were recorded.")
    st.caption(
        "Valid refreshed data can render with Review required when a drift "
        "threshold fails. Baselines are never rewritten automatically."
    )

    st.subheader("Field completeness")
    st.caption(
        "Missingness describes the 22-field cleaned full source. High missingness "
        "for electric_range_miles includes source zero classified as unknown."
    )
    st.plotly_chart(
        missingness_figure(data.missingness),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )
    with st.expander("View completeness data"):
        st.dataframe(
            _missingness_table(data.missingness),
            hide_index=True,
            width="stretch",
            column_config={
                "Missing rate": st.column_config.NumberColumn(format="percent")
            },
        )

    st.subheader("Data dictionary")
    st.caption("All 16 renamed source fields and six derived fields are listed.")
    with st.expander("View the 22-field dictionary", expanded=True):
        st.dataframe(
            _dictionary_table(data.field_definitions),
            hide_index=True,
            width="stretch",
        )

    left, right = st.columns(2)
    with left:
        st.subheader("Cleaning rules")
        for rule in data.cleaning_rules:
            st.write(f"- {rule}")
    with right:
        st.subheader("Analytical guardrails")
        for guardrail in data.analytical_guardrails:
            st.write(f"- {guardrail}")

    st.subheader("Project documentation")
    st.markdown(
        f"- [Public GitHub repository]({data.repository_url})\n"
        "- `docs/DATA_CONTRACT.md` — schema, validation, and cleaning policy\n"
        "- `docs/DATA_QUALITY.md` — metrics and baseline philosophy\n"
        "- `docs/EDA_FINDINGS.md` — findings and limitations\n"
        "- `docs/DASHBOARD_SPEC.md` — product/accessibility specification"
    )
