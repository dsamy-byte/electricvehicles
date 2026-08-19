# Exploratory Analysis Findings

These findings were generated reproducibly from the supplied 294,193-row
snapshot using `scripts/generate_eda_report.py`. The JSON artifact is generated
under `reports/generated` and is intentionally excluded from Git; the analysis
code, tests, and documented findings are version controlled.

## Interpretation boundary

This is a point-in-time population of vehicles currently registered through
Washington DOL. Model year is a vehicle attribute. Therefore:

- model-year counts are not annual sales;
- model-year counts are not annual registration events;
- the dataset alone cannot measure historical adoption or retention; and
- geographic fields describe the registered owner's listed location.

The dashboard should consistently use language such as “vehicles in the current
snapshot” and “model-year composition.”

## Population composition

- The snapshot contains 294,193 vehicles across model years 1999-2027; median
  model year is 2023.
- Model years 2021 and newer account for 231,201 vehicles, or 78.59% of the
  current population. This shows that the registered population skews toward
  recent model years, not that 78.59% were registered after 2020.
- BEVs account for 237,567 vehicles (80.75%); PHEVs account for 56,626 (19.25%).
- The population spans 49 makes and 198 model labels.

## Manufacturer and model concentration

- Tesla accounts for 120,899 vehicles (41.10%), substantially more than the
  next-ranked make, Chevrolet at 19,964 (6.79%).
- The ten leading makes account for 82.42% of the full population.
- Tesla Model Y is the leading model with 64,984 vehicles (22.09%), followed by
  Model 3 with 38,980 (13.25%) and Nissan Leaf with 13,368 (4.54%).
- Model Y and Model 3 together represent 35.34% of all records, making model
  concentration a stronger story than a simple manufacturer ranking alone.

## Geographic concentration

- King County contains 141,971 records (48.26%).
- The five leading counties—King, Snohomish, Pierce, Clark, and Thurston—contain
  79.15% of all vehicles.
- Seattle is the leading city with 44,697 records (15.19%), followed by Bellevue
  at 14,151 (4.81%) and Vancouver at 10,969 (3.73%).
- There are 257 distinct populated county labels and 941 city labels because
  Washington registrations can include owner addresses outside Washington.
  Geographic views must default clearly to Washington or expose the state
  filter rather than implying every place is inside the state.

Counts show where registered vehicles are concentrated, not an EV adoption
rate. Population or total-vehicle denominators would be required to compare
county penetration fairly.

## Range availability and selection bias

- Only 45,090 of 237,567 BEVs (18.98%) have a researched non-zero range in this
  snapshot. Among those known values, median range is 215 miles, the middle 50%
  spans 150-239 miles, mean is 200.46 miles, and maximum is 337 miles.
- 56,613 of 56,626 PHEVs (99.98%) have a known range. Their known median is 32
  miles, middle 50% is 22-38 miles, mean is 32.21 miles, and maximum is 153.
- Because known-range coverage differs drastically by vehicle type and likely
  by model year, range comparisons apply only to records with researched range.
  They must show coverage and must not be generalized to the full BEV fleet.

## CAFV eligibility

- CAFV eligibility is unknown for 192,477 vehicles (65.43%).
- 78,154 vehicles (26.57%) are labeled eligible.
- 23,562 vehicles (8.01%) are labeled not eligible because of low battery range.

Unknown status must remain its own category. Combining it with eligible or not
eligible would materially misrepresent the dataset.

## Recommended dashboard narratives

The evidence supports five primary narratives for the product specification:

1. **Current population overview:** total vehicles, BEV/PHEV mix, median model
   year, known-range coverage, and the active filter context.
2. **Model-year composition:** current fleet composition by model year, with a
   prominent note that this is not a historical adoption series.
3. **Market concentration:** make and model rankings, shares, and cumulative
   concentration, especially Tesla and its two leading models.
4. **Geographic concentration:** county/city distribution and maps, paired with
   state controls and an explicit warning that counts are not penetration rates.
5. **Range and eligibility transparency:** known-range distributions alongside
   coverage rates, plus CAFV's three categories without collapsing unknowns.

Data quality and methodology should be a persistent sixth supporting view so
users can inspect missingness, provenance, cleaning rules, and limitations.

## Reproduce the results

```powershell
python scripts/generate_eda_report.py `
  --data "path/to/electric.csv"
```

The command runs validated ingestion and cleaning before analysis and writes
`reports/generated/exploratory_analysis.json` by default.

