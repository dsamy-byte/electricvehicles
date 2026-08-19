# Project Memory

## Purpose

Build a polished Streamlit dashboard named `electricvehicles` for cleaning,
validating, analyzing, and visualizing Electric Vehicle Population Data using
sound software-engineering practices.

## Product decisions

- Application type: Streamlit web dashboard.
- Repository name: `electricvehicles`.
- GitHub visibility: public.
- GitHub repository: https://github.com/dsamy-byte/electricvehicles
- Initial audience: people exploring Washington electric-vehicle registrations.
- Planned analysis: overview metrics, adoption trends, manufacturer/model
  comparisons, geographic analysis, electric range, CAFV eligibility, and
  data-quality reporting.
- Raw and generated data will not be committed to Git.
- Preserve the source `Electric Range` value and create a separate cleaned
  value in which zero is treated as missing/unknown.

## Dataset snapshot

- Source working file: `Course Resurces/messy data 2/electric.csv`.
- Size at initial inspection: 80,508,789 bytes.
- Shape: 294,193 rows and 16 columns.
- Coverage: model years 1999-2027; 99.74% of records have state `WA`.
- Vehicle types: 80.75% BEV and 19.25% PHEV.
- No fully duplicated rows were detected in the initial profile.
- Known quality concerns include unknown CAFV eligibility, electric ranges
  encoded as zero, and small amounts of missing geographic information.

## Engineering decisions

- Use a `src` package layout.
- Keep data ingestion, validation, transformation, analysis, and presentation
  concerns separate.
- Use type hints, focused functions, automated tests, Ruff, and pytest.
- Keep code documentation thorough: modules explain responsibilities, public
  APIs document inputs/outputs/errors, policy-sensitive transformations explain
  their rationale, and tests document expected behavior.
- Use environment-based configuration for local data paths.
- Update this file as part of every completed task before committing.
- Use focused commits and push each completed task when GitHub is available.
- The complete implementation sequence and task definition of done live in
  `ROADMAP.md`; update that document if project scope or ordering changes.

## Completed

- Inspected and summarized the source dataset.
- Agreed on Streamlit, repository name, visibility, and initial dashboard scope.
- Created the initial project structure and engineering configuration.
- Initialized a standalone Git repository on the `main` branch.
- Verified that the Python source compiles successfully. Full pytest and Ruff
  checks await installation of the declared development dependencies.
- Created the public GitHub repository and pushed the project foundation.
- Documented the complete 17-task delivery roadmap and per-task completion
  checklist.
- Approved the electric-range policy: retain the raw value and represent zero
  as missing in a separate cleaned field.
- Defined the authoritative Data.WA source (`f6w7-q2d2`), ODbL 1.0 data
  license, supplied-snapshot fingerprint, full 16-column contract, validation
  severities, cleaning rules, baseline quality observations, and analytical
  guardrails in `docs/DATA_CONTRACT.md`.
- Added environment-aware path resolution, string-preserving CSV ingestion,
  duplicate/exact header checks, structured validation errors and warnings,
  machine-readable contract constants, and representative test fixtures.
- Installed project and development dependencies in the ignored `.venv`.
- Passed 12 automated tests plus Ruff lint and format checks.
- Validated the full 294,193-row supplied snapshot with zero blocking errors
  and eight expected missing-optional-value warnings.
- Implemented non-mutating data cleaning with explicit column mapping, nullable
  analysis types, identifier preservation, four-digit postal normalization,
  raw/analytical range separation, display categories, Washington flags, and
  parsed coordinates.
- Added comprehensive in-code documentation and documented the 22-column clean
  output schema.
- Passed all 21 tests plus Ruff checks. The full clean output contains 294,193
  rows, 192,490 analytically missing ranges, 294,183 normalized five-digit
  postal codes, and 294,175 complete coordinate pairs.
- Added immutable, JSON-serializable data-quality models covering completeness,
  cardinality, duplicates, range availability, coordinate coverage, Washington
  share, and validation warnings.
- Added a documented command-line report generator and a version-controlled
  baseline with tolerant, reviewable drift thresholds. Generated reports remain
  outside Git.
- Passed all 29 tests plus Ruff checks. The full snapshot passed all 13 baseline
  checks with 65.4298% unknown range, 99.9939% complete coordinates, and
  99.7413% Washington records.
- Added presentation-neutral, immutable exploratory-analysis models and a JSON
  generator for model-year composition, EV/CAFV mix, make/model rankings,
  geographic concentration, and known-range distributions.
- Passed all 38 tests plus Ruff checks and documented verified findings and five
  primary dashboard narratives in `docs/EDA_FINDINGS.md`.
- Key findings: BEVs are 80.75%; Tesla is 41.10%; the top five counties contain
  79.15%; model years 2021+ comprise 78.59% of this current snapshot; and known
  range covers only 18.98% of BEVs versus 99.98% of PHEVs.
- Analytical guardrail reinforced: model-year composition is not sales or
  historical adoption, geographic counts are not penetration rates, and range
  statistics must disclose known-value coverage.
- Defined the five-page dashboard architecture, global filter precedence,
  metric formulas, exact chart choices, responsive visual system, accessibility
  requirements, privacy rules, performance target, and all application states
  in `docs/DASHBOARD_SPEC.md`.
- Product decisions: default analytical location scope is Washington only;
  pages 1-4 share filters; Data Quality always describes the unfiltered source;
  maps aggregate repeated coordinates and never expose vehicle identifiers.
- Implemented the production Streamlit shell with local theme/CSS, stable
  five-page top navigation, cached pipeline loading keyed by file identity,
  cascading global filters, immutable page context, reset/empty states, and
  safe source/validation/baseline failures.
- Kept filtering and orchestration independent of Streamlit and documented all
  shell boundaries in `docs/APP_ARCHITECTURE.md`.
- Passed all 49 tests plus Ruff checks. A headless health probe and full-dataset
  Streamlit execution both passed; the real default view renders Washington
  scope across model years 1999-2027 without exceptions.
- Implemented the Overview page using a documented, immutable view model and
  reusable Streamlit-independent Plotly figure builders.
- Added five denominator-aware metrics, chronological model-year composition,
  semantic BEV/PHEV mix, top-five makes, narrative summaries, exact expandable
  tables, and the required point-in-time interpretation callout.
- Passed all 56 tests plus Ruff checks. Full-dataset Streamlit execution renders
  five metrics, three charts, and three accessible tables without exceptions;
  Washington-default metrics are 293,432 vehicles, 80.8% BEV, median model year
  2023, 34.6% known-range coverage, and 26.6% CAFV eligible.
- Updated all rendered components to Streamlit's current `width="stretch"` API
  so the Overview runs without known width deprecation warnings.
- Implemented the Makes & Models page with documented view models that treat a
  model as `(make, model)`, deterministic tie ordering, complete rankings,
  cumulative shares, and a zero-filled leading-make/model-year grid.
- Added separate Top 5/10/20 make and model controls, four Plotly views (make
  rank, model rank, concentration, heatmap), narrative summaries, exact tables,
  and explicit current-population interpretation guidance.
- Passed all 66 tests plus Ruff checks, including direct Streamlit execution of
  the market renderer. In the Washington-default population, 49 makes and 198
  make/model combinations are present; Tesla has 120,514 vehicles (41.07%), the
  top ten makes have 82.42%, and Model Y/Model 3 are the two leading models.
- Implemented the Geography page with documented full geographic identities,
  privacy-safe aggregate coordinate models, deterministic county/city rankings,
  coordinate coverage, Top 5/10/20 controls, search, narratives, and accessible
  tables.
- Enforced privacy structurally: map points expose state/county/city,
  approximate coordinates, and aggregate counts only—never DOL IDs or
  vehicle-level rows. The UI reiterates that counts are not penetration rates.
- Passed all 75 tests plus Ruff checks, including direct Geography rendering.
  Washington-default output contains 39 counties and 563 cities; King County
  has 141,971 vehicles (48.38%), 293,424 vehicles (99.9973%) have usable
  coordinates, and 908 aggregate map points are rendered.
- Implemented the Range & CAFV page with documented, pre-aggregated view models
  for known/unknown coverage, per-type distribution bins, known-value interval
  statistics, and all three CAFV categories.
- Added four headline metrics, four Plotly views, exact accessible tables, and
  explicit selection-bias guidance. Unknown range never becomes zero, Unknown
  CAFV remains separate, and BEV/PHEV statistics are never silently combined.
- Passed all 87 tests plus Ruff checks, including direct Range & CAFV rendering.
  Washington-default range coverage is 34.56% overall: 18.98% for 236,994 BEVs
  versus 99.98% for 56,438 PHEVs. Known medians are 215 miles for BEVs and 32
  miles for PHEVs; CAFV status is 65.44% Unknown and 26.57% Eligible.
- Implemented the unfiltered Data Quality and Methodology page with executable
  provenance constants, source size/SHA-256 fingerprinting, validation warnings,
  all baseline observations, 22-field missingness, the complete clean data
  dictionary, cleaning rules, analytical guardrails, attribution, and links.
- Enforced unfiltered quality structurally: its view model accepts cached full
  application artifacts rather than filtered page data. A test applies a filter
  that removes a row and proves the quality page still reports both source rows.
- Passed all 93 tests plus Ruff checks, including direct quality-page rendering.
  The full snapshot reports 294,193 rows, 22 clean fields, eight warnings, and
  13/13 passing baseline checks; its SHA-256 remains
  `1a8c3c6b0ff3b3068cd2471d898017dae5a70d63b3265ed95b78d4108d3645d9`.
- Completed release-oriented automated hardening with real Streamlit filter
  reruns, cascading-option assertions, missing-source and empty-result states,
  accessibility/privacy contract checks, and a cross-version GitHub Actions
  workflow covering Python 3.11 and 3.14.
- Added an 85% branch-coverage gate. All 99 tests pass with 90.59% measured
  branch coverage, and Ruff lint and formatting checks pass.
- Added a documented, machine-readable full-data benchmark. On the 294,193-row
  snapshot, the cold validated pipeline took 7.060 seconds; ordinary filter and
  page-view-model operations took 0.085-0.255 seconds, all below the one-second
  interaction target. Generated benchmark JSON remains outside Git.

## Current task

Task 14 is complete: the automated quality suite, CI matrix, failure and
interaction states, accessibility/privacy contracts, and full-data performance
benchmark are implemented and passing.

## Next task

Task 15: complete documentation and operational readiness, including setup,
usage, architecture, contribution guidance, screenshots, deployment guidance,
license selection, and dependency/secret-management review.

## Open decisions

- Choose an open-source license before the first public release.
- Choose the deployment platform later in the project.
- Decide whether the app will ship with a processed data artifact or retrieve
  data during deployment.
