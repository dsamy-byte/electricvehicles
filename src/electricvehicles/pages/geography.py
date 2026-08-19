"""Privacy-safe aggregate geography page for registered-owner locations.

The renderer receives only aggregate geographic view models for maps and
rankings. Vehicle identifiers are never passed into Plotly or displayed in
tables, and raw counts are explicitly distinguished from penetration rates.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import streamlit as st

from electricvehicles.application import PageContext
from electricvehicles.geography_data import (
    GeographyRank,
    MapPoint,
    build_geography_data,
)
from electricvehicles.ui.charts import aggregate_map_figure, geography_ranking_figure
from electricvehicles.ui.components import (
    render_empty_state,
    render_page_header,
)

TOP_N_OPTIONS = (5, 10, 20)


def _ranking_table(results: Sequence[GeographyRank]) -> pd.DataFrame:
    """Return exact place identities, counts, and shares for accessible display."""
    return pd.DataFrame(
        {
            "Rank": [result.rank for result in results],
            "State": [result.state for result in results],
            "County": [result.county for result in results],
            "City": [result.city for result in results],
            "Vehicles": [result.count for result in results],
            "Share": [result.share for result in results],
        }
    )


def _render_ranking_table(label: str, results: Sequence[GeographyRank]) -> None:
    """Render an expandable, keyboard-accessible place ranking table."""
    with st.expander(f"View {label} data"):
        st.dataframe(
            _ranking_table(results),
            hide_index=True,
            width="stretch",
            column_config={"Share": st.column_config.NumberColumn(format="percent")},
        )


def _map_table(points: Sequence[MapPoint], query: str) -> pd.DataFrame:
    """Build searchable aggregate map values without source identifiers."""
    table = pd.DataFrame(
        {
            "State": [point.state for point in points],
            "County": [point.county for point in points],
            "City": [point.city for point in points],
            "Vehicles": [point.count for point in points],
        }
    )
    if query.strip():
        needle = query.strip().casefold()
        searchable = (
            table["State"].astype("string")
            + " "
            + table["County"].astype("string")
            + " "
            + table["City"].astype("string")
        ).str.casefold()
        table = table.loc[searchable.str.contains(needle, regex=False)]
    return table.sort_values(
        ["Vehicles", "State", "County", "City"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)


def render(context: PageContext) -> None:
    """Render aggregate map, geographic metrics, rankings, and searchable data."""
    render_page_header(
        context=context,
        eyebrow="Registered-owner locations",
        title="Geography",
        description=(
            "Explore aggregate vehicle counts by state, county, city, and location."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return

    geography = build_geography_data(context.filtered_data)
    metrics = st.columns(4)
    metrics[0].metric(
        "States represented",
        f"{geography.state_count:,}",
        help="Populated registered-owner state codes after active filters.",
    )
    metrics[1].metric(
        "Counties represented",
        f"{geography.county_count:,}",
        help="Distinct (state, county) combinations after active filters.",
    )
    metrics[2].metric(
        "Cities represented",
        f"{geography.city_count:,}",
        help="Distinct (state, county, city) combinations after active filters.",
    )
    metrics[3].metric(
        "Leading county",
        geography.leading_county,
        help=(
            f"{geography.leading_county_count:,} vehicles, or "
            f"{geography.leading_county_share:.1%} of the filtered population."
        ),
    )

    st.subheader("Aggregate registered-owner locations")
    st.caption(
        f"{geography.coordinate_vehicle_count:,} vehicles "
        f"({geography.coordinate_coverage:.1%}) have usable approximate source "
        "coordinates. Markers combine vehicles at the same place and coordinate."
    )
    if geography.map_points:
        st.plotly_chart(
            aggregate_map_figure(geography.map_points),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
    else:
        st.info("No usable coordinates are available for the selected population.")

    county_tab, city_tab = st.tabs(("Counties", "Cities"))
    with county_tab:
        county_limit = st.segmented_control(
            "Number of counties",
            TOP_N_OPTIONS,
            default=10,
            key="geography_county_limit",
        )
        visible_counties = geography.county_rankings[: int(county_limit or 10)]
        st.plotly_chart(
            geography_ranking_figure(visible_counties),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leader = visible_counties[0]
        st.write(
            f"{leader.label} leads with {leader.count:,} vehicles "
            f"({leader.share:.1%} of the filtered population)."
        )
        _render_ranking_table("county ranking", visible_counties)

    with city_tab:
        city_limit = st.segmented_control(
            "Number of cities",
            TOP_N_OPTIONS,
            default=10,
            key="geography_city_limit",
        )
        visible_cities = geography.city_rankings[: int(city_limit or 10)]
        st.plotly_chart(
            geography_ranking_figure(visible_cities),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        leader = visible_cities[0]
        st.write(
            f"{leader.label} leads with {leader.count:,} vehicles ({leader.share:.1%})."
        )
        _render_ranking_table("city ranking", visible_cities)

    st.subheader("Search aggregate place data")
    query = st.text_input(
        "Search state, county, or city",
        key="geography_place_search",
        placeholder="For example: Seattle or King",
    )
    place_table = _map_table(geography.map_points, query)
    st.caption(f"{len(place_table):,} aggregate place-coordinate rows shown.")
    st.dataframe(place_table, hide_index=True, width="stretch")

    st.info(
        "Counts are not EV penetration rates: this source has no population or "
        "total-vehicle denominator. Coordinates are approximate registered-owner "
        "locations and are displayed only as aggregate place counts."
    )
