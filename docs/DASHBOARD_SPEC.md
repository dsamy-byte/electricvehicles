# Dashboard Product and Design Specification

This specification is the implementation contract for the Streamlit user
experience. It translates the verified exploratory findings and data caveats
into pages, controls, metrics, charts, interactions, visual rules, and states.

## Product goal

Help a general audience explore the composition and geographic concentration of
the Washington DOL electric-vehicle registration population without implying
that the snapshot contains sales history, annual registration activity, or EV
penetration rates.

## Primary audience and questions

The first release serves residents, students, analysts, and policymakers who
want clear answers to these questions:

1. How many vehicles are in the selected current-registration population?
2. What is the BEV/PHEV and model-year composition?
3. Which makes and models dominate the selected population?
4. Where are registered-owner locations concentrated?
5. What does the source say about electric range and CAFV eligibility?
6. How complete and reliable are the fields behind each result?

The application is exploratory and informational. It does not forecast,
recommend purchases, estimate charging demand, or claim causal relationships.

## Information architecture

The app uses five pages in this order:

1. **Overview** — orientation, headline metrics, model-year composition, EV mix,
   and leading makes.
2. **Makes & Models** — rankings, market concentration, and model-year/make
   composition.
3. **Geography** — registered-owner location counts, county/city rankings, and
   an aggregated map.
4. **Range & CAFV** — known-range coverage and distributions plus all three
   CAFV categories.
5. **Data Quality** — provenance, validation status, missingness, baseline
   checks, cleaning rules, definitions, and analytical limitations.

The page names are user-facing. Python modules and reusable components should
use stable snake-case names independent of navigation labels.

## Global filter model

Filters live in the sidebar and apply consistently to pages 1-4. The Data
Quality page describes the complete unfiltered source and clearly ignores
analytical filters.

| Filter | Control | Default | Behavior |
| --- | --- | --- | --- |
| Location scope | Segmented/radio control | Washington only | `WA` or all source states; never silently removes out-of-state records. |
| Model year | Inclusive range slider | Full available range | Options update from the loaded snapshot. |
| EV type | Multiselect | BEV and PHEV | Uses short display codes with full definitions nearby. |
| Make | Searchable multiselect | All | Options narrow after location/year/type filters. |
| County | Searchable multiselect | All | Options narrow after upstream filters; labels remain source values. |
| CAFV status | Multiselect | Eligible, Not eligible, Unknown | Unknown remains selected and cannot be silently folded into another status. |

Filter order is deterministic: location, model year, EV type, make, county,
then CAFV. A prominent **Reset filters** action restores defaults. Empty
multiselects mean “all available,” not “none,” unless Streamlit behavior makes
that ambiguous; helper text must state the chosen convention.

Every analytical page displays a compact context line such as:

> Washington only · Model years 1999-2027 · All EV types · All makes

Metric calculations and chart titles always refer to the filtered population.
Downloads, if added later, must include filter metadata.

## Shared metric definitions

| Metric | Definition | Display rule |
| --- | --- | --- |
| Vehicles | Count of distinct `dol_vehicle_id` values after filters | Whole number with thousands separators. |
| BEV share | BEV vehicle count divided by filtered vehicle count | One decimal percent; show denominator in help text. |
| Median model year | Median `model_year` in filtered population | One decimal only when median is not integral. |
| Known-range coverage | Non-null `electric_range_miles` divided by filtered vehicle count | One decimal percent; never display unknown range as zero. |
| Eligible share | `Eligible` count divided by filtered vehicle count | One decimal percent; helper text states Unknown is included in denominator. |
| Category share | Category count divided by all filtered rows | One decimal percent and count in tooltip. |

If a denominator is zero, the UI displays an em dash and an explanation; it
never displays `0%`, `NaN`, or an exception.

## Page 1 — Overview

### Purpose

Give users an accurate orientation to the selected current population in one
screen and provide obvious paths into deeper pages.

### Layout

1. Title, one-sentence scope statement, source-update/snapshot context, and
   active-filter summary.
2. Five metric cards: Vehicles, BEV share, Median model year, Known-range
   coverage, and Eligible share.
3. Full-width model-year composition column chart.
4. Two-column row: EV-type horizontal bar and top-five-makes horizontal bar.
5. A concise “Read this correctly” callout explaining the point-in-time model.

### Chart rules

- Model-year bars use chronological order, integer ticks, and vehicle counts.
- A subtitle says “Current population by vehicle model year—not annual sales.”
- EV-type and make charts use horizontal bars because labels and comparisons
  are clearer than pie/donut slices.
- Every chart supports hover details with count and share and has a text summary
  immediately before or after it for screen-reader and low-vision users.

## Page 2 — Makes & Models

### Purpose

Explain manufacturer/model concentration while supporting detailed comparison.

### Layout and interactions

1. Metrics: distinct makes, distinct models, leading make/share, and top-ten
   make concentration.
2. Tabs or adjacent panels for **Makes** and **Models**, each with a ranked
   horizontal bar chart and Top 5/10/20 control.
3. Cumulative concentration line by ranked make with 50%, 75%, and 90% guides.
4. Model-year × make heatmap limited to user-selected leading makes.
5. Accessible data table containing the exact chart values and shares.

Ranking ties sort alphabetically after count. The model ranking must display the
make alongside model when filtering permits duplicate model names across makes;
analysis code should group by `(make, model)` for that view.

## Page 3 — Geography

### Purpose

Show where registered-owner locations are concentrated without overstating
precision or presenting raw counts as adoption rates.

### Layout and interactions

1. Metrics: states represented, counties represented, cities represented, and
   leading county/share.
2. Aggregated point map using repeated source coordinates grouped into one
   marker with vehicle count; no vehicle-level points or owner identifiers.
3. County and city ranked horizontal bars.
4. Searchable table with state, county, city, vehicle count, and population
   share.
5. Persistent note: “Counts are not EV penetration rates; no population or
   total-vehicle denominator is present.”

Coordinates are approximate registered-owner locations and often repeat. Map
tooltips show aggregate place/count only. The map must not imply exact household
locations. Out-of-state records use the same rules and are visible only when the
location scope includes them.

## Page 4 — Range & CAFV

### Purpose

Make range availability and CAFV classification understandable without hiding
the source's unusually high unknown rate.

### Layout and interactions

1. Metrics by selected population: known-range coverage, median known range,
   CAFV eligible share, and CAFV unknown share.
2. Separate BEV and PHEV coverage bars showing known versus unknown counts.
3. Known-range histogram faceted or selectable by EV type; zeros never appear
   because they are unknown, not measured range.
4. Box/interval summary for known values with count and coverage adjacent.
5. Three-category CAFV horizontal bar: Eligible, Not eligible, Unknown.
6. Methodology callout explaining selection bias in known BEV range.

BEV/PHEV range distributions must not share a single unexplained aggregate.
Every distribution displays known-value count and coverage. The UI explicitly
states that known-range statistics do not characterize records with unknown
range.

## Page 5 — Data Quality

### Purpose

Make provenance and limitations inspectable rather than burying them in a
footer.

### Layout

1. Source identity, publisher, dataset ID, snapshot row count/checksum context,
   ODbL link, and source link.
2. Validation summary: blocking errors, warnings, and baseline status.
3. Baseline-check table with metric, observation, expectation, and status.
4. Missingness chart and table for all fields.
5. Expandable data dictionary, cleaning rules, and analytical guardrails.
6. Links to project documentation and GitHub repository.

Quality status uses icon + text + color. Green/red alone is never the only
signal. The page describes full-source quality even when analytical filters are
active and says so explicitly.

## Visual system

### Design character

The dashboard should feel civic, modern, and calm: information-dense enough for
analysis, with generous spacing and restrained decoration. Avoid automotive
marketing imagery, neon “electric” effects, gradients behind data, and chart
styles that compete with values.

### Color tokens

Final colors must pass WCAG AA contrast in their actual context. Starting
tokens for implementation and browser verification:

| Token | Hex | Intended use |
| --- | --- | --- |
| Ink | `#14213D` | Primary text and dark chart labels |
| Muted ink | `#52606D` | Secondary text on white |
| Canvas | `#F6F8FB` | App background |
| Surface | `#FFFFFF` | Cards and chart panels |
| Border | `#D9E2EC` | Dividers and card outlines |
| Electric blue | `#1769AA` | Primary series/actions |
| Teal | `#147D78` | Secondary series/positive neutral |
| Amber | `#B26A00` | Unknown/warning categories |
| Red | `#B42318` | Errors/not eligible when semantically required |
| Green | `#287D3C` | Passed/eligible when semantically required |

BEV and PHEV keep the same colors on every page. Unknown CAFV/range uses amber
plus a text label or pattern distinction. Eligible/not eligible colors are not
reused for unrelated ranking series.

### Typography and spacing

- Use Streamlit's accessible sans-serif stack; do not load remote fonts.
- Base text is at least 16 px; helper text is at least 14 px.
- Use a restrained type scale and no more than three heading levels per page.
- Use an 8 px spacing rhythm, 12-16 px card radius, and subtle borders instead
  of heavy shadows.
- Numbers use tabular alignment where available.

## Responsive behavior

- Wide screens: up to five metric cards in one row and two-column chart groups.
- Medium screens: metric cards wrap predictably; chart groups become one column
  when labels would compress.
- Narrow screens: single-column flow, full-width controls, no horizontal page
  scrolling, and tables use contained scrolling only when unavoidable.
- Chart height adapts to category count with a documented min/max instead of
  squeezing labels.
- The map receives a usable minimum height but never prevents access to its
  equivalent table.

## Accessibility requirements

1. Meet WCAG 2.2 AA contrast for text, controls, focus, and chart marks where
   practical within Streamlit/Plotly.
2. Never encode meaning through color alone; use labels, icons, ordering, or
   patterns as a second signal.
3. Give every control a visible label and useful help text.
4. Use descriptive headings in logical order and avoid decorative emoji in
   semantic headings.
5. Provide chart-adjacent summaries and accessible value tables.
6. Ensure keyboard access and visible focus states for navigation and filters.
7. Format large numbers and percentages consistently; avoid unexplained
   abbreviations.
8. Respect reduced-motion preferences and avoid automatic animation.
9. Do not rely on hover as the only way to retrieve a value.
10. Verify at 200% browser zoom and common mobile widths during Task 14.

## Application states

### Loading

- Show a clear “Loading and validating vehicle data…” status.
- Avoid fake progress percentages because CSV parsing duration is not known.
- Cache successful immutable pipeline results by file identity/update time.

### Success with warnings

- Render analytical pages when validation has only non-blocking warnings.
- Show a compact warning summary linked to Data Quality, not repeated alarm
  banners on every chart.

### Empty filter result

- Keep filter controls and active context visible.
- Replace metrics/charts with one clear message: “No vehicles match these
  filters.”
- Offer Reset filters; never display misleading zero-filled charts.

### Missing or unreadable data

- Show the actionable loader message, expected path/configuration, and a link to
  setup instructions.
- Do not expose a Python traceback to users.

### Blocking validation failure

- Stop analytical rendering.
- List concise contract failures and direct users to Data Quality/methodology.
- Preserve diagnostic detail in developer logs without exposing sensitive data.

### Baseline drift

- Valid data may render with a prominent “Review required” quality status.
- Identify failed metrics and expectations; never automatically rewrite the
  baseline or suppress the observed values.

## Performance and architecture constraints

- Run ingestion, validation, cleaning, quality, and analysis outside page
  rendering functions.
- Cache the loaded/cleaned dataframe and reusable aggregates with Streamlit
  resource/data caching appropriate to mutability.
- Apply one shared filter function so pages cannot disagree about semantics.
- Pre-aggregate map points before passing data to Plotly.
- Avoid recomputing full-data quality for each filter interaction.
- Keep charts in presentation modules; core analysis remains Streamlit-free.
- Do not add a database until profiling demonstrates that the CSV/Parquet path
  cannot meet the interaction target.

Initial performance target: after the first load, ordinary filter interactions
should update visible results within one second on the development machine.

## Privacy and responsible display

- Never reconstruct or expose a full VIN.
- Do not expose DOL Vehicle IDs in UI tables or downloads.
- Never plot individual vehicle records as exact household points.
- Aggregate map locations and suppress identifiers from tooltips.
- Retain source attribution and ODbL requirements on the methodology page.

## Acceptance criteria for UI implementation

Task 7 is implemented successfully when Tasks 8-13 can be built without an
unresolved decision about navigation, filtering, metrics, chart type, color
semantics, accessibility, error states, or analytical wording. Deviations from
this specification must be recorded in `PROJECT_MEMORY.md` with rationale.

