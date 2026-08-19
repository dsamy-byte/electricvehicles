"""Application orchestration shared by the Streamlit entry point and pages.

This module owns immutable page context and pipeline composition, while UI
rendering remains in ``ui`` and ``pages`` modules. Keeping orchestration free of
Streamlit makes its behavior directly testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from electricvehicles.cleaning import load_clean_data
from electricvehicles.filtering import FilterSelection, apply_filters
from electricvehicles.quality import DataQualityReport, build_quality_report
from electricvehicles.validation import ValidationReport


@dataclass(frozen=True)
class LoadedApplicationData:
    """Full-snapshot artifacts that are safe to cache between page reruns."""

    clean_data: pd.DataFrame
    validation_report: ValidationReport
    quality_report: DataQualityReport
    source_path: Path


@dataclass(frozen=True)
class PageContext:
    """Full and filtered state supplied to one dashboard page renderer."""

    application: LoadedApplicationData
    filters: FilterSelection
    filtered_data: pd.DataFrame


def load_application_data(path: str | Path) -> LoadedApplicationData:
    """Run the validated pipeline and build unfiltered quality artifacts.

    Args:
        path: Resolved source CSV path. Streamlit caching wraps this function at
            the UI boundary with file size and modification time as cache keys.

    Returns:
        Clean data, validation warnings, baseline results, and source identity.
    """
    source_path = Path(path).resolve()
    cleaned, validation = load_clean_data(source_path)
    quality = build_quality_report(cleaned, validation)
    return LoadedApplicationData(cleaned, validation, quality, source_path)


def build_page_context(
    application: LoadedApplicationData, selection: FilterSelection
) -> PageContext:
    """Apply global filters and package immutable state for page renderers."""
    return PageContext(
        application=application,
        filters=selection,
        filtered_data=apply_filters(application.clean_data, selection),
    )
