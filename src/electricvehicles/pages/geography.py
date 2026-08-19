"""Geography page shell; content arrives in roadmap Task 11."""

from electricvehicles.application import PageContext
from electricvehicles.ui.components import (
    render_empty_state,
    render_implementation_placeholder,
    render_page_header,
)


def render(context: PageContext) -> None:
    """Render the shared shell for registered-owner location analysis."""
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
    render_implementation_placeholder("Task 11: Geographic analysis")
