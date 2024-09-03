# pylint: disable=invalid-name,duplicate-code
"""Streamlit app for the main UI"""

import streamlit as st

if "select" in st.session_state:
    st.session_state.select = st.session_state.select

st.set_page_config(
    page_title="Assistant",
    page_icon="⚡",
)

st.sidebar.markdown("# 💬 Analytical Assistant")

st.markdown(
    """
    # 💬 Analytical Assistant
    **👈 Select a persona from the sidebar** to see it in action!
    ### Business Analyst
    This is for people with limited/no coding (SQL) experience.
    - Just ask a question in natural language and let the AI do the work for you.
    - Code is generated based on your question in the backend.
    - The analysis will be created for you.
    ### Data Analyst
    This is for people with some coding (SQL) experience, who want help with their queries.
    - Ask questions to generate the code
    - Run it to check your intuition.
    - Create basic visualizations as well.
    ### Data Catalogue
    Check column descriptions and example data rows to get a feel of the different tables.
"""
)
