# Data Contract and Provenance

This document defines the source, meaning, expected structure, validation
policy, and cleaning policy for data used by the Electric Vehicles Dashboard.
It is the contract for the ingestion and cleaning code implemented in later
tasks.

## Authoritative source

- Dataset: [Electric Vehicle Population Data][wa-data]
- Publisher and data owner: Washington State Department of Licensing (DOL),
  published through Data.WA
- Dataset identifier: `f6w7-q2d2`
- Scope: BEVs and PHEVs currently registered through Washington State DOL
- First published: October 19, 2023
- Official CSV export: [Data.WA CSV download][csv-export]
- Catalog metadata: [Data.gov catalog entry][data-gov]
- Source data license: [Open Data Commons Open Database License 1.0][odbl]

The source is a point-in-time population, not a vehicle-sales dataset or a
historical registration-event dataset. Model-year counts must not be described
as annual sales or annual registrations. The publisher refreshes the dataset,
so row counts and category values can change.

The ODbL applies to the source database. Attribution and applicable ODbL
requirements must be preserved when publicly using or redistributing the data
or a derivative database. A separate code license will be chosen before the
project's first release.

## Supplied snapshot

The local source inspected on August 19, 2026 is intentionally stored outside
this Git repository.

| Property | Value |
| --- | --- |
| Working path | `../Course Resurces/messy data 2/electric.csv` |
| Expected project path | `data/raw/electric.csv` |
| Size | 80,508,789 bytes |
| Rows | 294,193 |
| Columns | 16 |
| SHA-256 | `1a8c3c6b0ff3b3068cd2471d898017dae5a70d63b3265ed95b78d4108d3645d9` |
| Official catalog update near inspection | August 13, 2026 |

The supplied file matches the official schema. Its checksum has not been
independently matched to an archived official export, so the project must not
claim that its precise retrieval time is known. Future source snapshots are
valid when they satisfy this contract; they are not expected to retain this
row count or checksum.

## Row grain and identity

Each row represents one vehicle in the published current-registration
population. `DOL Vehicle ID` is the row/entity key for this dataset snapshot
and must be non-null, positive, and unique.

`VIN (1-10)` contains only the first ten VIN characters. It is deliberately
not unique and must never be used as the entity key or presented as a complete
VIN.

## Source schema

All input column names are required. Nullable means the loader accepts a blank
source value and the cleaning layer represents it as missing.

| Source column | Clean name | Logical type | Nullable | Meaning and contract |
| --- | --- | --- | --- | --- |
| `VIN (1-10)` | `vin_prefix` | string | No | First 10 VIN characters; uppercase VIN alphabet excluding I, O, and Q. |
| `County` | `county` | string | Yes | Registered owner's county; may be outside Washington. |
| `City` | `city` | string | Yes | Registered owner's city. |
| `State` | `state` | string | No | Two-character uppercase US state/territory-style code from the source. |
| `Postal Code` | `postal_code` | string | Yes | Postal identifier, normally five digits; never numeric analysis data. |
| `Model Year` | `model_year` | integer | No | VIN-decoded model year; plausible range is 1886 through current year plus two. |
| `Make` | `make` | category/string | No | VIN-decoded manufacturer. New values are allowed. |
| `Model` | `model` | category/string | No | VIN-decoded vehicle model. New values are allowed. |
| `Electric Vehicle Type` | `ev_type` | category | No | Exactly BEV or PHEV under the source labels documented below. |
| `Clean Alternative Fuel Vehicle (CAFV) Eligibility` | `cafv_eligibility` | category | No | Source eligibility classification; exactly one documented label below. |
| `Electric Range` | `electric_range_raw` | nullable integer | Yes | Publisher's electric-only range in miles; must be non-negative. Zero means unknown for analysis. |
| `Legislative District` | `legislative_district` | nullable integer/category | Yes | Washington legislative district, 1 through 49 when present. |
| `DOL Vehicle ID` | `dol_vehicle_id` | integer/string identifier | No | Positive DOL identifier; unique within a snapshot and not a measurement. |
| `Vehicle Location` | `vehicle_location` | nullable WKT point | Yes | Approximate source location formatted as `POINT (longitude latitude)`. |
| `Electric Utility` | `electric_utility` | string/category | Yes | Utility or utility combination serving the registered location. |
| `2020 Census Tract` | `census_tract_2020` | string | Yes | Eleven-digit 2020 census tract GEOID; never numeric analysis data. |

### Allowed vehicle-type labels

- `Battery Electric Vehicle (BEV)`
- `Plug-in Hybrid Electric Vehicle (PHEV)`

### Allowed CAFV labels in this contract version

- `Clean Alternative Fuel Vehicle Eligible`
- `Not eligible due to low battery range`
- `Eligibility unknown as battery range has not been researched`

A new vehicle type is a contract error until reviewed. A new CAFV label is a
contract error until reviewed because it may change the interpretation of
eligibility metrics. New makes, models, places, and utilities are expected and
must not fail ingestion.

## Validation policy

Validation occurs before and after cleaning. Failures that make analysis
unsafe stop the pipeline; quality concerns that remain interpretable generate
warnings and appear in the quality report.

### Blocking errors

- The file cannot be found, decoded as UTF-8 with optional BOM, or parsed as CSV.
- Required columns are missing, duplicated, or unexpectedly renamed.
- The dataset has no data rows.
- A required field is blank.
- `DOL Vehicle ID` is invalid, non-positive, or duplicated.
- Model year or electric range cannot be parsed as an integer.
- Model year is implausible or electric range is negative.
- VIN prefix does not contain exactly ten valid uppercase VIN characters.
- Vehicle type or CAFV eligibility contains an unreviewed label.

### Quality warnings

- Optional fields are missing.
- A postal code is not four or five digits before normalization.
- A legislative district is outside 1-49 or missing for a Washington record.
- A census tract is not exactly eleven digits.
- A location is not a valid WKT point or has invalid longitude/latitude bounds.
- The proportion of missing or unknown values changes materially from the
  recorded baseline.
- Row count, categories, or model-year coverage changes unexpectedly.

## Cleaning policy

Cleaning is deterministic and audit-friendly. The raw source is immutable.

1. Normalize column names to the clean names in the schema table.
2. Trim surrounding whitespace and convert empty strings to missing values.
3. Preserve identifiers as strings where leading zeros or numeric operations
   would be misleading (`postal_code`, `census_tract_2020`, and VIN prefix).
4. Left-pad a four-digit numeric postal code with one zero; retain valid
   five-digit codes. Flag other formats instead of guessing.
5. Parse integer fields with nullable integer types where appropriate.
6. Preserve `electric_range_raw`. Create `electric_range_miles`, converting a
   source value of zero to missing because zero represents unavailable or
   unresearched range in this dataset. Never silently impute a range.
7. Preserve the full CAFV source label and optionally derive a short display
   label through an explicit mapping.
8. Parse `vehicle_location` into separate nullable `longitude` and `latitude`
   fields while retaining the source WKT value.
9. Do not discard out-of-state records. Expose state filtering and explain
   that Washington registrations may have owner addresses elsewhere.
10. Do not drop incomplete records by default. Exclude them only from metrics
    requiring the missing field, and report the relevant denominator.
11. Do not deduplicate on VIN prefix. Exact duplicate rows or duplicate DOL IDs
    stop the pipeline for review rather than being silently removed.

## Baseline quality observations

These observations describe only the supplied snapshot and will become
machine-generated quality checks in Task 5.

- No exact duplicate rows; all 294,193 DOL Vehicle IDs are unique.
- 192,477 electric-range values are zero and therefore become analytically
  missing under the approved policy.
- Electric range has 13 source blanks and no negative values.
- Legislative district has 762 blanks; vehicle location has 18 blanks.
- County, city, postal code, electric utility, and census tract each have 10
  blanks.
- Five populated postal codes have four digits and require leading-zero
  normalization.
- All populated census tract values contain eleven digits.
- All populated vehicle locations match the expected WKT point shape.
- The snapshot contains 52 state codes and is 99.74% Washington records.

## Analytical guardrails

- Refer to rows as vehicles or current registration-population records, not
  people, sales, purchases, or historical registration events.
- Model year is a vehicle attribute, not the date the vehicle was registered.
- Counts by model year show the model-year composition of the current snapshot,
  not annual adoption on their own.
- Unknown electric range and unknown CAFV status must remain visible; they must
  not be treated as zero range, ineligible, or eligible.
- Geographic charts describe the registered owner's listed location, subject
  to missing and out-of-state records.
- Always show filter context and denominators for percentages.

[wa-data]: https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/data
[csv-export]: https://data.wa.gov/api/v3/views/f6w7-q2d2/export.csv?accessType=DOWNLOAD
[data-gov]: https://catalog.data.gov/dataset/electric-vehicle-population-data
[odbl]: https://opendatacommons.org/licenses/odbl/1-0/

