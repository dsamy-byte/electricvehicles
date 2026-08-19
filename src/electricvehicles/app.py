"""Streamlit entry point for the Electric Vehicles dashboard."""

import streamlit as st


def main() -> None:
    """Render the initial application shell."""
    st.set_page_config(
        page_title="Electric Vehicles Dashboard",
        page_icon="⚡",
        layout="wide",
    )
    st.title("Electric Vehicles Dashboard")
    st.info("The tested data pipeline and dashboard are under development.")


if __name__ == "__main__":
    main()

