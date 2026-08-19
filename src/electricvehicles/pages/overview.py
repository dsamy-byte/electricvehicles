"""Overview page shell; analytical content arrives in roadmap Task 9."""

from electricvehicles.application import PageContext
from electricvehicles.ui.components import (
    render_empty_state,
    render_implementation_placeholder,
    render_page_header,
)


def render(context: PageContext) -> None:
    """Render overview framing, filter context, and current incremental state."""
    render_page_header(
        context=context,
        eyebrow="Current registration population",
        title="Electric Vehicles Overview",
        description=(
            "Explore the composition of electric vehicles currently registered "
            "through Washington State DOL."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return
    render_implementation_placeholder("Task 9: Overview and adoption trends")
