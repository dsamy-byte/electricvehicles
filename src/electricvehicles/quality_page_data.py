"""Presentation-neutral provenance and methodology page view models.

The Data Quality page always describes the complete loaded source, never the
sidebar-filtered population. This module converts validation and quality objects
into immutable display records while keeping source definitions, cleaning
decisions, and interpretation rules centrally documented.
"""

from __future__ import annotations

from dataclasses import dataclass

from electricvehicles.application import LoadedApplicationData
from electricvehicles.data_contract import (
    CLEAN_FIELD_DEFINITIONS,
    DATA_LICENSE_NAME,
    DATA_LICENSE_URL,
    DATASET_ID,
    DATASET_NAME,
    DATASET_PUBLISHER,
    DATASET_URL,
    PROJECT_REPOSITORY_URL,
    FieldDefinition,
)


@dataclass(frozen=True)
class MissingnessResult:
    """Missing-value count and rate for one clean dataframe column."""

    column: str
    missing_count: int
    missing_rate: float
    populated_count: int


@dataclass(frozen=True)
class BaselineResult:
    """User-facing baseline observation, expectation, and status."""

    metric: str
    observed: float | int
    expectation: str
    status: str


@dataclass(frozen=True)
class QualityPageData:
    """Immutable source, quality, dictionary, and methodology page content."""

    dataset_name: str
    publisher: str
    dataset_id: str
    dataset_url: str
    license_name: str
    license_url: str
    repository_url: str
    source_file_name: str
    source_size_bytes: int
    source_sha256: str
    row_count: int
    column_count: int
    warning_count: int
    baseline_passed_count: int
    baseline_check_count: int
    baseline_passed: bool
    validation_warnings: tuple[str, ...]
    baseline_results: tuple[BaselineResult, ...]
    missingness: tuple[MissingnessResult, ...]
    field_definitions: tuple[FieldDefinition, ...]
    cleaning_rules: tuple[str, ...]
    analytical_guardrails: tuple[str, ...]


CLEANING_RULES = (
    "Trim surrounding text and collapse repeated internal whitespace.",
    "Preserve identifiers as strings and pad four-digit numeric postal codes.",
    "Preserve raw range and make source zero missing in the analysis field.",
    "Map EV and CAFV labels without discarding their full source labels.",
    "Parse valid WKT into coordinates while retaining the source WKT field.",
    "Keep incomplete and out-of-state rows unless a metric needs a missing field.",
    "Never deduplicate on VIN prefix or silently remove duplicate DOL IDs.",
)

ANALYTICAL_GUARDRAILS = (
    "Rows are vehicles in a current registration population, not people or sales.",
    "Model year is not registration date; model-year charts are not adoption history.",
    "Unknown range and CAFV status never become measured zero or ineligible.",
    "Range statistics describe known values and disclose coverage by EV type.",
    "Geographic counts are listed owner locations, not EV penetration rates.",
    "Maps use aggregate approximate places and never expose DOL vehicle IDs.",
    "Shares disclose their full-source or filtered denominator and filter context.",
)


def build_quality_page_data(application: LoadedApplicationData) -> QualityPageData:
    """Build unfiltered provenance, quality, and methodology page content.

    Args:
        application: Cached full-source artifacts. Filtered page context is not
            accepted, preventing sidebar filters from altering quality results.

    Returns:
        Immutable display content ordered deterministically for charts/tables.
    """
    quality = application.quality_report
    missingness = tuple(
        sorted(
            (
                MissingnessResult(
                    column=column,
                    missing_count=profile.missing_count,
                    missing_rate=profile.missing_rate,
                    populated_count=quality.row_count - profile.missing_count,
                )
                for column, profile in quality.columns.items()
            ),
            key=lambda item: (-item.missing_rate, item.column.casefold()),
        )
    )
    baseline_results = tuple(
        BaselineResult(
            metric=check.metric,
            observed=check.observed,
            expectation=check.expectation,
            status="Passed" if check.passed else "Review required",
        )
        for check in quality.baseline_checks
    )
    passed_count = sum(result.status == "Passed" for result in baseline_results)
    return QualityPageData(
        dataset_name=DATASET_NAME,
        publisher=DATASET_PUBLISHER,
        dataset_id=DATASET_ID,
        dataset_url=DATASET_URL,
        license_name=DATA_LICENSE_NAME,
        license_url=DATA_LICENSE_URL,
        repository_url=PROJECT_REPOSITORY_URL,
        source_file_name=application.source_path.name,
        source_size_bytes=application.source_size_bytes,
        source_sha256=application.source_sha256,
        row_count=quality.row_count,
        column_count=quality.column_count,
        warning_count=len(quality.validation_warnings),
        baseline_passed_count=passed_count,
        baseline_check_count=len(baseline_results),
        baseline_passed=quality.is_within_baseline,
        validation_warnings=quality.validation_warnings,
        baseline_results=baseline_results,
        missingness=missingness,
        field_definitions=CLEAN_FIELD_DEFINITIONS,
        cleaning_rules=CLEANING_RULES,
        analytical_guardrails=ANALYTICAL_GUARDRAILS,
    )
