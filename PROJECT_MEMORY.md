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

## Current task

Task 3 is complete: reproducible ingestion and validation are implemented and
verified against fixtures and the full supplied snapshot.

## Next task

Task 4: implement deterministic cleaning and feature preparation with tests for
every approved transformation and edge case.

## Open decisions

- Choose an open-source license before the first public release.
- Choose the deployment platform later in the project.
- Decide whether the app will ship with a processed data artifact or retrieve
  data during deployment.
