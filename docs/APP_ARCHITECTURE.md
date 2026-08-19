# Application Shell Architecture

Task 8 establishes the production Streamlit shell while intentionally leaving
page-specific analytical bodies to Tasks 9-13.

## Runtime flow

1. `app.py` configures the page and loads local version-controlled CSS.
2. `get_data_path()` resolves an explicit environment override or the default
   `data/raw/electric.csv` location.
3. File size and modification time form the Streamlit cache identity.
4. The pipeline loads, validates, cleans, and builds full-source quality results
   once per file identity.
5. The shared sidebar builds cascading filter selections.
6. Presentation-independent filtering creates a copied analytical dataframe.
7. `PageContext` gives every page the same full-source and filtered state.
8. Stable top-navigation URLs select one of five page renderers.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `app.py` | Streamlit boundary, cache wrapper, safe failures, and navigation |
| `application.py` | Pipeline orchestration and immutable page context |
| `filtering.py` | Testable filter semantics, options, and context descriptions |
| `ui/sidebar.py` | Cascading Streamlit controls and filter reset behavior |
| `ui/components.py` | Shared headers, empty states, placeholders, and local styles |
| `pages/*.py` | Page-specific rendering, implemented incrementally in Tasks 9-13 |
| `assets/styles.css` | Local responsive and focus-visible visual refinements |
| `.streamlit/config.toml` | Theme, browser telemetry, and headless server defaults |

Core loading, cleaning, validation, quality, analysis, and filtering logic does
not import Streamlit. This keeps calculations reusable and directly testable.

## Cache behavior

The cleaned dataframe and full quality report use `st.cache_data`. Cache keys
include the resolved source path, byte size, and nanosecond modification time.
Replacing the CSV at the same path therefore invalidates stale results without
requiring a manual cache clear.

Page filters are not part of full-pipeline caching. They apply to the cached
clean dataframe, which avoids re-reading and re-validating 294,193 rows during
ordinary interactions. Full-source quality is calculated once and deliberately
does not change with sidebar filters.

## Filter behavior

The default scope is Washington only. Year bounds are inclusive. Empty EV type,
make, county, and CAFV multiselects mean all available values. Options cascade
in this order:

1. location scope;
2. model year;
3. EV type;
4. make;
5. county; and
6. CAFV status.

Stale downstream values are removed if an upstream selection makes them
unavailable. Every analytical page receives the same `FilterSelection` and
filtered copy. The Data Quality page reads only full-source artifacts.

## Error and empty states

- Missing/unreadable files show setup guidance without a traceback.
- Blocking validation errors stop analytical rendering and show contract
  failures.
- Baseline configuration errors stop rendering with an actionable message.
- Non-blocking data warnings permit analysis and remain available through the
  full quality report.
- Empty filtered populations retain controls and show a reset-oriented message
  instead of zero-filled charts.

Unexpected programming errors are not swallowed by a broad exception handler;
they remain visible during development and testing rather than masquerading as
source-data problems.

## Verification

- 49 automated tests pass, including filtering, application orchestration, and
  an end-to-end Streamlit `AppTest` execution.
- Ruff lint and formatting checks pass.
- A headless server health probe returns `ok`.
- Full-dataset `AppTest` execution renders `Electric Vehicles Overview` with
  Washington-only scope, model years 1999-2027, and no application exceptions.

The Overview, Makes & Models, and Geography renderers are now implemented. Their
business aggregations remain in `overview_data.py`, `market_data.py`, and
`geography_data.py`; page modules compose controls, figures, narratives, search,
and accessible tables only. Geography map models contain aggregate place counts
and coordinates but no DOL identifiers or vehicle-level records.
