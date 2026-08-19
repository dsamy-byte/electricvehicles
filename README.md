# Electric Vehicles Dashboard

A polished Streamlit application for exploring Washington State electric
vehicle registration data. The planned dashboard will cover adoption trends,
manufacturers and models, geographic distribution, electric range, CAFV
eligibility, and source-data quality.

## Project status

The validated data pipeline, quality reporting, exploratory analysis,
application shell and all five specified pages are implemented incrementally
with automated tests. Quality hardening, documentation, deployment, and release
work continue according to the project roadmap.
See [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md) for the current project state and
next task. See [`ROADMAP.md`](ROADMAP.md) for the complete task-by-task delivery
plan and the definition of done used at each checkpoint.

The source schema, provenance, validation expectations, cleaning rules, and
analytical limitations are defined in
[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md).

## Local setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install the project and development tools:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

4. Place the source file at `data/raw/electric.csv`. Raw and generated data
   are intentionally excluded from Git.
5. Run the application:

   ```powershell
   streamlit run src/electricvehicles/app.py
   ```

## Development checks

```powershell
pytest
ruff check .
ruff format --check .
```

## Validated ingestion

The loader resolves `EV_DATA_PATH` relative to the project root, preserves raw
CSV values as nullable strings, verifies the published header before pandas can
rename duplicate columns, and separates blocking contract errors from
non-blocking quality warnings:

```python
from electricvehicles.ingestion import load_validated_data

raw_data, validation_report = load_validated_data()
for warning in validation_report.warnings:
    print(warning)
```

See [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) for the rules enforced by
the validation layer.

For analysis-ready values, use the supported end-to-end pipeline:

```python
from electricvehicles.cleaning import load_clean_data

clean_data, validation_report = load_clean_data()
```

It returns the 16 renamed source fields and six documented derived fields while
retaining auditable raw range and location values.

## Data-quality report

Generate the machine-readable quality report with:

```powershell
python scripts/generate_quality_report.py
```

The command compares the current snapshot with version-controlled drift
thresholds and writes ignored JSON output under `reports/generated`. See
[`docs/DATA_QUALITY.md`](docs/DATA_QUALITY.md) for metrics and interpretation.

## Reproducible exploratory analysis

Generate the presentation-neutral exploratory results with:

```powershell
python scripts/generate_eda_report.py
```

The verified findings, limitations, and recommended dashboard narratives are in
[`docs/EDA_FINDINGS.md`](docs/EDA_FINDINGS.md).

The approved page architecture, filters, metric definitions, visual system,
accessibility requirements, and application states are documented in
[`docs/DASHBOARD_SPEC.md`](docs/DASHBOARD_SPEC.md).

The implemented shell's runtime flow, caching, filtering, module boundaries,
and failure behavior are documented in
[`docs/APP_ARCHITECTURE.md`](docs/APP_ARCHITECTURE.md).

The Overview page currently provides five denominator-aware metrics,
model-year composition, EV-type mix, leading makes, explanatory narratives, and
expandable value tables. Its calculations remain separate from Streamlit in
`overview_data.py`, while reusable Plotly styling lives in `ui/charts.py`.

The Makes & Models page provides separate Top 5/10/20 rankings, make/model-safe
identity, cumulative manufacturer concentration, a leading-make/model-year
heatmap, narratives, and exact accessible tables. Its tested aggregations live
in `market_data.py`.

The Geography page provides full-identity county/city rankings, aggregate
registered-owner location markers, coordinate coverage, search, narratives,
and accessible tables. `geography_data.py` guarantees that map view models do
not contain vehicle identifiers.

The Range & CAFV page keeps known/unknown coverage explicit, separates BEV and
PHEV distributions, displays known-value interval summaries, preserves all CAFV
statuses, and provides exact accessible tables. Its histogram data is
pre-aggregated in `range_cafv_data.py` rather than passed as vehicle rows.

The unfiltered Data Quality page exposes authoritative provenance, the loaded
file fingerprint, validation warnings, all baseline checks, 22-field
missingness, the executable data dictionary, cleaning rules, analytical
guardrails, license attribution, and project links.

## Data source

The working dataset is the Electric Vehicle Population Data file supplied for
this project. Source provenance and retrieval instructions will be documented
during the data-pipeline task.
