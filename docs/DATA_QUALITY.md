# Data-Quality Reporting

The project measures data quality after validated ingestion and deterministic
cleaning. Quality reporting observes data; it never repairs, drops, or imputes
records.

## Run the report

With the source file at the configured path:

```powershell
python scripts/generate_quality_report.py
```

Or provide explicit paths:

```powershell
python scripts/generate_quality_report.py `
  --data "path/to/electric.csv" `
  --output "reports/generated/data_quality.json"
```

The output directory is excluded from Git because each JSON report describes a
particular local source snapshot. The baseline configuration at
`config/quality_baseline.json` is version controlled.

The command exits with code `0` when all baseline checks pass and code `2` when
valid data has materially drifted outside at least one threshold. Ingestion or
contract failures remain errors and stop report generation.

## Metrics

The JSON report includes:

- row and column counts;
- exact duplicated-row and duplicated-DOL-ID counts;
- missing count, missing rate, and non-null cardinality for every clean column;
- unknown electric-range count and rate;
- complete coordinate count and rate;
- Washington vehicle count and share;
- warnings from source validation; and
- every baseline expectation, observed value, and pass/fail result.

Rates are proportions from `0.0` to `1.0` and are rounded to six decimal places.
Counts and rates are both retained so consumers do not need to infer the
denominator.

## Baseline philosophy

The initial baseline represents the supplied August 2026 snapshot. It is a
drift detector, not a frozen copy of that file:

- row count may move by 20% in either direction;
- optional-field missingness has explicit maximum rates;
- duplicated rows and DOL identifiers remain disallowed;
- unknown-range rate may move by 10 percentage points; and
- Washington share may move by 2 percentage points.

These thresholds allow routine publisher refreshes while surfacing changes that
could invalidate dashboard assumptions. A baseline failure does not erase the
report or disguise the observed metrics. It should trigger investigation before
deployment. Baselines must only be changed through a reviewed commit with a
documented reason; they must never be automatically rewritten from new data.

## Initial full-snapshot result

The report generated during Task 5 contained 13 checks, all passing:

| Metric | Result |
| --- | ---: |
| Rows | 294,193 |
| Validation warnings | 8 |
| Exact duplicate rows | 0 |
| Duplicate DOL IDs | 0 |
| Unknown electric range | 65.4298% |
| Complete coordinate pairs | 99.9939% |
| Washington records | 99.7413% |

The eight warnings are the expected optional-field missingness warnings already
recorded in the data contract and project memory.

