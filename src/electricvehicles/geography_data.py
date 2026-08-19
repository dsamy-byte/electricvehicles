"""Privacy-safe geographic aggregations for the Geography dashboard page.

The source contains approximate registered-owner locations. This module never
returns DOL vehicle identifiers or vehicle-level map records. Map points are
grouped by place and repeated source coordinate, while rankings retain state and
county context so same-named places are not accidentally merged.

Geographic counts describe concentration in the current registration snapshot.
They are not EV penetration rates because population and total-vehicle
denominators are outside this dataset.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class GeographyRank:
    """One ranked county or city with full geographic identity."""

    rank: int
    label: str
    state: str
    county: str | None
    city: str | None
    count: int
    share: float


@dataclass(frozen=True)
class MapPoint:
    """Aggregate count at one approximate source coordinate and place."""

    state: str
    county: str
    city: str
    longitude: float
    latitude: float
    count: int


@dataclass(frozen=True)
class GeographyData:
    """Immutable metrics, rankings, and aggregate points for filtered data."""

    vehicle_count: int
    state_count: int
    county_count: int
    city_count: int
    leading_county: str
    leading_county_count: int
    leading_county_share: float
    coordinate_vehicle_count: int
    coordinate_coverage: float
    county_rankings: tuple[GeographyRank, ...]
    city_rankings: tuple[GeographyRank, ...]
    map_points: tuple[MapPoint, ...]


def _rank_geographies(
    grouped: pd.Series,
    *,
    total: int,
    level: str,
) -> tuple[GeographyRank, ...]:
    """Convert grouped place counts into deterministic full-identity ranks."""
    rows: list[tuple[str, str | None, str | None, int]] = []
    for key, count in grouped.items():
        if level == "county":
            state, county = key
            rows.append((str(state), str(county), None, int(count)))
        else:
            state, county, city = key
            rows.append((str(state), str(county), str(city), int(count)))
    rows.sort(
        key=lambda item: (
            -item[3],
            (item[2] or item[1] or "").casefold(),
            item[0].casefold(),
            (item[1] or "").casefold(),
        )
    )

    results: list[GeographyRank] = []
    for rank, (state, county, city, count) in enumerate(rows, start=1):
        label = f"{county}, {state}" if city is None else f"{city}, {state}"
        results.append(
            GeographyRank(
                rank=rank,
                label=label,
                state=state,
                county=county,
                city=city,
                count=count,
                share=round(count / total, 6),
            )
        )
    return tuple(results)


def _aggregate_map_points(frame: pd.DataFrame) -> tuple[MapPoint, ...]:
    """Aggregate complete place/coordinate rows without retaining identifiers."""
    columns = ["state", "county", "city", "longitude", "latitude"]
    located = frame.dropna(subset=columns)
    grouped = (
        located.groupby(columns, observed=True, dropna=False)
        .size()
        .sort_values(ascending=False)
    )
    return tuple(
        MapPoint(
            state=str(state),
            county=str(county),
            city=str(city),
            longitude=float(longitude),
            latitude=float(latitude),
            count=int(count),
        )
        for (state, county, city, longitude, latitude), count in grouped.items()
    )


def build_geography_data(frame: pd.DataFrame) -> GeographyData:
    """Calculate geographic metrics, rankings, and aggregate map points.

    Args:
        frame: Non-empty analysis-ready dataframe after global filters.

    Returns:
        Immutable geographic results containing no vehicle identifiers.

    Raises:
        ValueError: If required clean columns are missing, the filtered frame is
            empty, or no populated county/city geography remains.
    """
    required = {
        "dol_vehicle_id",
        "state",
        "county",
        "city",
        "longitude",
        "latitude",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Geography analysis requires clean columns: {missing}")
    if frame.empty:
        raise ValueError("Geography analysis requires at least one filtered vehicle.")

    vehicle_count = int(frame["dol_vehicle_id"].nunique(dropna=True))
    counties = frame.dropna(subset=["state", "county"])
    cities = frame.dropna(subset=["state", "county", "city"])
    if counties.empty or cities.empty:
        raise ValueError(
            "Geography analysis requires populated county and city values."
        )

    county_counts = counties.groupby(["state", "county"], observed=True).size()
    city_counts = cities.groupby(["state", "county", "city"], observed=True).size()
    county_rankings = _rank_geographies(
        county_counts, total=vehicle_count, level="county"
    )
    city_rankings = _rank_geographies(city_counts, total=vehicle_count, level="city")
    map_points = _aggregate_map_points(frame)
    coordinate_vehicle_count = sum(point.count for point in map_points)
    leader = county_rankings[0]
    return GeographyData(
        vehicle_count=vehicle_count,
        state_count=int(frame["state"].nunique(dropna=True)),
        county_count=len(county_rankings),
        city_count=len(city_rankings),
        leading_county=leader.label,
        leading_county_count=leader.count,
        leading_county_share=leader.share,
        coordinate_vehicle_count=coordinate_vehicle_count,
        coordinate_coverage=round(coordinate_vehicle_count / vehicle_count, 6),
        county_rankings=county_rankings,
        city_rankings=city_rankings,
        map_points=map_points,
    )
