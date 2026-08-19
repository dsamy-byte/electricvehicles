"""Benchmark cold loading and cached-interaction analytical work.

The command intentionally uses the production pipeline and presentation-neutral
view-model builders against the configured full CSV. It writes machine-readable
JSON so measurements can be compared between development machines and dataset
snapshots. Timings are elapsed wall-clock seconds from ``perf_counter`` and are
benchmarks, not flaky CI assertions.

Run from the repository root with::

    python scripts/benchmark_pipeline.py

Set ``EV_DATA_PATH`` when the source is not at the documented default path.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from time import perf_counter
from typing import TypeVar

from electricvehicles.application import build_page_context, load_application_data
from electricvehicles.config import get_data_path
from electricvehicles.filtering import FilterSelection
from electricvehicles.geography_data import build_geography_data
from electricvehicles.market_data import build_market_data
from electricvehicles.overview_data import build_overview_data
from electricvehicles.quality_page_data import build_quality_page_data
from electricvehicles.range_cafv_data import build_range_cafv_data

T = TypeVar("T")
OUTPUT_PATH = Path("reports/generated/performance.json")
INTERACTION_TARGET_SECONDS = 1.0


def _measure(operation: Callable[[], T]) -> tuple[T, float]:
    """Return an operation's result and high-resolution elapsed wall time."""
    started = perf_counter()
    result = operation()
    return result, perf_counter() - started


def main() -> None:
    """Run one reproducible full-snapshot benchmark and write its measurements."""
    source_path = get_data_path()
    application, cold_load = _measure(lambda: load_application_data(source_path))

    years = application.clean_data["model_year"].dropna()
    selection = FilterSelection(
        washington_only=True,
        model_year_min=int(years.min()),
        model_year_max=int(years.max()),
    )
    context, filter_time = _measure(lambda: build_page_context(application, selection))
    builders: dict[str, Callable[[], object]] = {
        "overview_view_model": lambda: build_overview_data(context.filtered_data),
        "market_view_model": lambda: build_market_data(context.filtered_data),
        "geography_view_model": lambda: build_geography_data(context.filtered_data),
        "range_cafv_view_model": lambda: build_range_cafv_data(context.filtered_data),
        "quality_view_model": lambda: build_quality_page_data(application),
    }
    interaction_times = {"filter": filter_time}
    for name, builder in builders.items():
        _, interaction_times[name] = _measure(builder)

    report = {
        "source": {
            "path": str(application.source_path),
            "rows": len(application.clean_data),
            "size_bytes": application.source_size_bytes,
            "sha256": application.source_sha256,
        },
        "seconds": {
            "cold_pipeline_load": cold_load,
            **interaction_times,
        },
        "interaction_target_seconds": INTERACTION_TARGET_SECONDS,
        "interaction_target_passed": all(
            elapsed <= INTERACTION_TARGET_SECONDS
            for elapsed in interaction_times.values()
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
