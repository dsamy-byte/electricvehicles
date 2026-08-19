"""Generate a JSON quality report for an Electric Vehicle source snapshot.

Run from the project root after installing the package::

    python scripts/generate_quality_report.py

Use ``--data`` to override ``EV_DATA_PATH`` and ``--output`` to choose another
generated-report location. The command exits with status 2 if the valid dataset
has materially drifted outside the version-controlled baseline.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from electricvehicles.cleaning import load_clean_data
from electricvehicles.quality import build_quality_report, write_quality_report


def parse_args() -> argparse.Namespace:
    """Parse documented command-line options for report generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, help="Optional source CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/generated/data_quality.json"),
        help="JSON destination relative to the project root by default.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the validated cleaning and quality pipeline, then write JSON."""
    args = parse_args()
    cleaned, validation = load_clean_data(args.data)
    report = build_quality_report(cleaned, validation)
    output = write_quality_report(report, args.output)
    print(f"Quality report written to {output}")
    print(
        f"Rows: {report.row_count:,}; warnings: "
        f"{len(report.validation_warnings)}; baseline passed: "
        f"{report.is_within_baseline}"
    )
    return 0 if report.is_within_baseline else 2


if __name__ == "__main__":
    raise SystemExit(main())
