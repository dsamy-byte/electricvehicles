"""Machine-readable constants for the source-data contract."""

from __future__ import annotations

SOURCE_COLUMNS = (
    "VIN (1-10)",
    "County",
    "City",
    "State",
    "Postal Code",
    "Model Year",
    "Make",
    "Model",
    "Electric Vehicle Type",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility",
    "Electric Range",
    "Legislative District",
    "DOL Vehicle ID",
    "Vehicle Location",
    "Electric Utility",
    "2020 Census Tract",
)

REQUIRED_VALUE_COLUMNS = (
    "VIN (1-10)",
    "State",
    "Model Year",
    "Make",
    "Model",
    "Electric Vehicle Type",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility",
    "DOL Vehicle ID",
)

EV_TYPES = frozenset(
    {
        "Battery Electric Vehicle (BEV)",
        "Plug-in Hybrid Electric Vehicle (PHEV)",
    }
)

CAFV_LABELS = frozenset(
    {
        "Clean Alternative Fuel Vehicle Eligible",
        "Not eligible due to low battery range",
        "Eligibility unknown as battery range has not been researched",
    }
)
