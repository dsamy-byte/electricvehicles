"""Generate reusable JSON containing the exploratory-analysis results.

Example from the project root::

    python scripts/generate_eda_report.py --data path/to/electric.csv

The output describes the model-year composition of a current vehicle
population. It does not represent historical sales or annual registrations.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from electricvehicles.analysis import build_exploratory_analysis
from electricvehicles.cleaning import load_clean_data
from electricvehicles.config import PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    """Parse source and output paths for the reproducible analysis command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, help="Optional source CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/generated/exploratory_analysis.json"),
        help="JSON destination relative to the project root by default.",
    )
    return parser.parse_args()


def main() -> int:
    """Run ingestion, validation, cleaning, and exploratory aggregation."""
    args = parse_args()
    cleaned, _ = load_clean_data(args.data)
    analysis = build_exploratory_analysis(cleaned)
    output = args.output
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{analysis.to_json()}\n", encoding="utf-8")
    print(f"Exploratory analysis written to {output.resolve()}")
    print(
        f"Vehicles: {analysis.vehicle_count:,}; model years: "
        f"{analysis.model_year_min}-{analysis.model_year_max}; "
        f"makes: {analysis.make_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
