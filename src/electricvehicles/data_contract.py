"""Machine-readable constants for the Electric Vehicle data contract.

The human-readable contract lives in ``docs/DATA_CONTRACT.md``. Constants in
this module are the executable counterpart used by ingestion, validation, and
cleaning. Keeping them centralized prevents those layers from silently
disagreeing about source columns or controlled vocabularies.
"""

from __future__ import annotations

from dataclasses import dataclass

DATASET_NAME = "Electric Vehicle Population Data"
DATASET_PUBLISHER = "Washington State Department of Licensing (DOL)"
DATASET_ID = "f6w7-q2d2"
DATASET_URL = (
    "https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/data"
)
DATA_LICENSE_NAME = "Open Data Commons Open Database License 1.0"
DATA_LICENSE_URL = "https://opendatacommons.org/licenses/odbl/1-0/"
PROJECT_REPOSITORY_URL = "https://github.com/dsamy-byte/electricvehicles"


@dataclass(frozen=True)
class FieldDefinition:
    """User-facing definition of one analysis-ready dataframe field."""

    clean_name: str
    source_name: str
    logical_type: str
    nullable: bool
    description: str


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

# Executable dictionary covering the 16 renamed source fields and six derived
# fields. The Data Quality page renders these same definitions.
CLEAN_FIELD_DEFINITIONS = (
    FieldDefinition(
        "vin_prefix",
        "VIN (1-10)",
        "string",
        False,
        "First ten VIN characters; not a unique or complete VIN.",
    ),
    FieldDefinition("county", "County", "string", True, "Owner's listed county."),
    FieldDefinition("city", "City", "string", True, "Owner's listed city."),
    FieldDefinition(
        "state", "State", "string", False, "Owner's two-character state code."
    ),
    FieldDefinition(
        "postal_code",
        "Postal Code",
        "string",
        True,
        "Text postal identifier, normalized to five digits when possible.",
    ),
    FieldDefinition(
        "model_year",
        "Model Year",
        "nullable integer",
        False,
        "VIN-decoded model year; not a registration date.",
    ),
    FieldDefinition("make", "Make", "string", False, "Vehicle manufacturer."),
    FieldDefinition("model", "Model", "string", False, "Vehicle model label."),
    FieldDefinition(
        "ev_type",
        "Electric Vehicle Type",
        "string",
        False,
        "Full BEV or PHEV source classification.",
    ),
    FieldDefinition(
        "cafv_eligibility",
        "CAFV Eligibility",
        "string",
        False,
        "Full source CAFV eligibility label.",
    ),
    FieldDefinition(
        "electric_range_raw",
        "Electric Range",
        "nullable integer",
        True,
        "Auditable source electric range; zero means unresearched.",
    ),
    FieldDefinition(
        "legislative_district",
        "Legislative District",
        "nullable integer",
        True,
        "Washington legislative district from 1 through 49.",
    ),
    FieldDefinition(
        "dol_vehicle_id",
        "DOL Vehicle ID",
        "string identifier",
        False,
        "Unique snapshot key; never displayed as a vehicle field.",
    ),
    FieldDefinition(
        "vehicle_location",
        "Vehicle Location",
        "WKT point string",
        True,
        "Approximate source point retained for auditability.",
    ),
    FieldDefinition(
        "electric_utility",
        "Electric Utility",
        "string",
        True,
        "Utility or utility combination serving the listed location.",
    ),
    FieldDefinition(
        "census_tract_2020",
        "2020 Census Tract",
        "string identifier",
        True,
        "Eleven-digit census tract GEOID retained as text.",
    ),
    FieldDefinition(
        "electric_range_miles",
        "Derived",
        "nullable integer",
        True,
        "Analysis range with source zero converted to missing.",
    ),
    FieldDefinition(
        "ev_type_code", "Derived", "string", False, "Short code: BEV or PHEV."
    ),
    FieldDefinition(
        "cafv_status",
        "Derived",
        "string",
        False,
        "Display status: Eligible, Not eligible, or Unknown.",
    ),
    FieldDefinition(
        "is_washington",
        "Derived",
        "boolean",
        False,
        "Whether the normalized state code equals WA.",
    ),
    FieldDefinition(
        "longitude",
        "Derived from Vehicle Location",
        "nullable float",
        True,
        "Longitude parsed from a valid approximate WKT point.",
    ),
    FieldDefinition(
        "latitude",
        "Derived from Vehicle Location",
        "nullable float",
        True,
        "Latitude parsed from a valid approximate WKT point.",
    ),
)
