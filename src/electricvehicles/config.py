"""Project configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "electric.csv"


def get_data_path(explicit_path: str | Path | None = None) -> Path:
    """Return the configured raw-data path as an absolute path.

    An explicit path takes precedence over ``EV_DATA_PATH``. Relative paths
    are resolved from the project root so behavior does not depend on the
    process working directory.
    """
    configured = explicit_path or os.getenv("EV_DATA_PATH")
    path = Path(configured).expanduser() if configured else DEFAULT_DATA_PATH
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()
