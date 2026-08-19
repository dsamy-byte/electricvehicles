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

## Completed

- Inspected and summarized the source dataset.
- Agreed on Streamlit, repository name, visibility, and initial dashboard scope.
- Created the initial project structure and engineering configuration.
- Initialized a standalone Git repository on the `main` branch.
- Verified that the Python source compiles successfully. Full pytest and Ruff
  checks await installation of the declared development dependencies.
- Created the public GitHub repository and pushed the project foundation.

## Current task

Task 1 is complete. The project foundation is committed locally and pushed to
GitHub.

## Next task

Define the dataset schema, cleaning rules, validation behavior, and source-data
provenance before implementing the tested data pipeline.

## Open decisions

- Choose an open-source license before the first public release.
- Choose the deployment platform later in the project.
- Decide whether the app will ship with a processed data artifact or retrieve
  data during deployment.
