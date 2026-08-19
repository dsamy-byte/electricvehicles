# Electric Vehicles Dashboard

A polished Streamlit application for exploring Washington State electric
vehicle registration data. The planned dashboard will cover adoption trends,
manufacturers and models, geographic distribution, electric range, CAFV
eligibility, and source-data quality.

## Project status

The project foundation is in place. Data cleaning, analysis, visualization,
and the dashboard will be implemented incrementally with automated tests.
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

## Data source

The working dataset is the Electric Vehicle Population Data file supplied for
this project. Source provenance and retrieval instructions will be documented
during the data-pipeline task.
