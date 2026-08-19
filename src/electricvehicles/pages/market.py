"""Makes and models page shell; content arrives in roadmap Task 10."""

from electricvehicles.application import PageContext
from electricvehicles.ui.components import (
    render_empty_state,
    render_implementation_placeholder,
    render_page_header,
)


def render(context: PageContext) -> None:
    """Render the shared shell for manufacturer and model analysis."""
    render_page_header(
        context=context,
        eyebrow="Market composition",
        title="Makes & Models",
        description=(
            "Compare manufacturer and model concentration in the selected population."
        ),
    )
    if context.filtered_data.empty:
        render_empty_state()
        return
    render_implementation_placeholder("Task 10: Makes and models")
