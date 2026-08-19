# Quality Assurance

## Automated gates

The project requires Ruff lint and formatting checks plus pytest on every push
and pull request. The GitHub Actions matrix covers Python 3.11, the minimum
supported version, and Python 3.14, the current maximum. Pytest enforces at
least 85% branch coverage of the `electricvehicles` package.

The suite covers ingestion and contract failures, cleaning policies, quality
baselines, analytical aggregations, chart construction, all five page
renderers, full-shell execution, real filter reruns, cascading options, missing
source behavior, and empty results. Static regression tests preserve visible
keyboard focus, chart-associated exact-data tables, and the privacy-safe map
model. These tests supplement rather than replace manual keyboard,
screen-reader, contrast, responsive-layout, and browser checks.

## Performance benchmark

Run `python scripts/benchmark_pipeline.py` with `EV_DATA_PATH` pointing to the
full source snapshot. The script exercises the production validated pipeline,
Washington-default filtering, and every presentation-neutral page view model.
It records source identity and elapsed wall-clock seconds in the ignored
`reports/generated/performance.json` file. Results vary by hardware and current
system load, so measurements are recorded rather than asserted in CI.

Reference run on 2026-08-19 against 294,193 rows and the documented SHA-256:

| Operation | Seconds |
| --- | ---: |
| Cold ingestion, validation, cleaning, quality, and hashing | 7.060 |
| Washington-default filter | 0.085 |
| Overview view model | 0.130 |
| Makes & Models view model | 0.173 |
| Geography view model | 0.255 |
| Range & CAFV view model | 0.192 |
| Data Quality view model | <0.001 |

All ordinary interaction operations were below the one-second target. The cold
load occurs before Streamlit caches the full-snapshot artifacts and is reported
separately from subsequent filter interactions.
