"""Range and CAFV page shell; content arrives in roadmap Task 12."""

from electricvehicles.application import PageContext
from electricvehicles.ui.components import (
    render_empty_state,
    render_implementation_placeholder,
    render_page_header,
)


def render(context: PageContext) -> None:
    """Render the shared shell for range coverage and CAFV analysis."""
    render_page_header(
        context=context,
        eyebrow="Availability and eligibility",
        title="Range & CAFV",
        description=(
            "Interpret known electric range and all CAFV source categories responsibly."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return
    render_implementation_placeholder("Task 12: Range, vehicle type, and CAFV")
