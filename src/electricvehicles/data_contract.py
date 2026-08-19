"""Machine-readable constants for the Electric Vehicle data contract.

The human-readable contract lives in ``docs/DATA_CONTRACT.md``. Constants in
this module are the executable counterpart used by ingestion, validation, and
cleaning. Keeping them centralized prevents those layers from silently
disagreeing about source columns or controlled vocabularies.
"""

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

# Renaming is explicit instead of algorithmic because source labels include
# abbreviations and a year whose intended clean spelling should remain stable.
COLUMN_RENAMES = {
    "VIN (1-10)": "vin_prefix",
    "County": "county",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Model Year": "model_year",
    "Make": "make",
    "Model": "model",
    "Electric Vehicle Type": "ev_type",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility": "cafv_eligibility",
    "Electric Range": "electric_range_raw",
    "Legislative District": "legislative_district",
    "DOL Vehicle ID": "dol_vehicle_id",
    "Vehicle Location": "vehicle_location",
    "Electric Utility": "electric_utility",
    "2020 Census Tract": "census_tract_2020",
}

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

EV_TYPE_CODES = {
    "Battery Electric Vehicle (BEV)": "BEV",
    "Plug-in Hybrid Electric Vehicle (PHEV)": "PHEV",
}

CAFV_DISPLAY_LABELS = {
    "Clean Alternative Fuel Vehicle Eligible": "Eligible",
    "Not eligible due to low battery range": "Not eligible",
    "Eligibility unknown as battery range has not been researched": "Unknown",
}
