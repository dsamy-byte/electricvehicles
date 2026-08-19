# Project Roadmap

This roadmap is the agreed implementation sequence for the Electric Vehicles
Dashboard. Work proceeds one task at a time. Every completed task must include
appropriate verification, an update to `PROJECT_MEMORY.md`, a focused Git
commit, and a push to GitHub.

## Definition of done for every task

1. The scoped change is implemented without unrelated changes.
2. Relevant tests, static checks, or manual verification pass.
3. User-facing and technical documentation is updated when applicable.
4. `PROJECT_MEMORY.md` records decisions, results, and the next task.
5. The change is committed with a focused message and pushed to `main`.

## Phase 1: Foundation

### Task 1 — Project and repository setup

- Create the standalone project and `src` package layout.
- Configure Streamlit, dependencies, pytest, and Ruff.
- Protect secrets and exclude raw/generated data from Git.
- Create the project memory, README, Git repository, and public GitHub remote.

Status: complete.

## Phase 2: Data engineering

### Task 2 — Data contract and provenance

- Document the authoritative data source, retrieval date, and license/terms.
- Define all source columns, types, meanings, nullability, and constraints.
- Define identifier, categorical, numeric, and geographic handling.
- Record explicit cleaning rules and validation expectations.

Status: complete.

### Task 3 — Reproducible ingestion and validation

- Add configuration for locating the raw source file.
- Implement typed ingestion without modifying the original data.
- Validate required columns, types, allowed categories, and key constraints.
- Produce actionable errors for invalid or missing inputs.
- Add unit tests for valid and invalid fixtures.

Status: complete.

### Task 4 — Cleaning and feature preparation

- Normalize column names and categorical text consistently.
- Preserve source values where auditability is useful.
- Convert zero electric range to missing in a separate cleaned field while
  retaining the original field.
- Handle missing geographic values and identifier types deliberately.
- Derive only documented, reproducible analysis fields.
- Add tests for every cleaning rule and edge case.

Status: complete.

### Task 5 — Data-quality reporting

- Measure completeness, uniqueness, validity, and consistency.
- Report missing values, anomalous values, duplicates, and category drift.
- Make quality results available to both developers and dashboard users.
- Establish baseline quality expectations for future datasets.

Status: complete.

## Phase 3: Analysis and product design

### Task 6 — Exploratory data analysis

- Analyze registrations over time, vehicle types, makes, and models.
- Analyze electric range and CAFV eligibility with known limitations.
- Analyze county and city distributions and geographic concentration.
- Identify findings, caveats, and candidate dashboard narratives.

Status: complete.

### Task 7 — Dashboard specification and visual design

- Define information architecture, pages, filters, metrics, and charts.
- Establish visual theme, responsive behavior, and accessibility standards.
- Define empty, loading, warning, and error states.
- Confirm the specification before full UI implementation.

Status: complete.

## Phase 4: Application implementation

### Task 8 — Application shell and shared components

- Implement navigation, layout, theme, configuration, and reusable components.
- Add cached data loading and clear failure behavior.
- Keep presentation separate from data and analysis logic.

Status: complete.

### Task 9 — Overview and adoption trends

- Add headline metrics and time-based adoption views.
- Add global filters and explain metric definitions.

Status: complete.

### Task 10 — Makes and models

- Add manufacturer and model rankings, comparisons, and drill-downs.
- Ensure charts remain readable across filtering combinations.

### Task 11 — Geographic analysis

- Add county/city analysis and an appropriate interactive map.
- Handle missing or out-of-state records transparently.

### Task 12 — Range, vehicle type, and CAFV analysis

- Compare BEV and PHEV populations.
- Visualize known electric ranges without treating unknown zeros as real range.
- Explain CAFV eligibility and its unknown category.

### Task 13 — Data-quality and methodology page

- Present dataset scope, provenance, cleaning rules, quality metrics, and caveats.
- Give users enough context to interpret every dashboard result responsibly.

## Phase 5: Quality, delivery, and release

### Task 14 — Complete automated quality suite

- Expand unit and integration coverage for data and application logic.
- Run formatting, linting, and relevant type checks.
- Test representative UI states and failure paths.
- Check performance against the full dataset.

### Task 15 — Documentation and operational readiness

- Complete setup, usage, architecture, and contribution documentation.
- Add screenshots and deployment instructions.
- Decide on and add an open-source license.
- Review dependency and secret-management practices.

### Task 16 — Deployment

- Select and configure a hosting platform.
- Configure data availability and secrets safely.
- Add automated verification/deployment where appropriate.
- Perform a production smoke test.

### Task 17 — Release

- Complete final acceptance testing.
- Resolve release-blocking accessibility, correctness, and performance issues.
- Create a version tag and release notes.
- Record future enhancements in a prioritized backlog.
