# pylint: disable=invalid-name,duplicate-code
"""Streamlit app for the main UI"""

import streamlit as st

from bq_manager.query import BQManager
from config_manager.manager import Params

if "select" in st.session_state:
    st.session_state.select = st.session_state.select

st.set_page_config(
    page_title="Assistant",
    page_icon="⚡",
)


@st.cache_resource
def init_setup_dc() -> tuple[Params, BQManager]:
    """Setup the page"""
    confs = Params("./configs/config.yml")
    return (
        confs,
        BQManager(confs),
    )


configs, bqm = init_setup_dc()

st.sidebar.markdown("# 🌸 Data Catalogue")

st.markdown(
    """
    # 🌸 Data Catalogue

    #### Select a table :+1:!
    """
)


def reset_dfs() -> None:
    """Reset dataframes on selectbox change"""
    if "descriptions" in st.session_state:
        del st.session_state.descriptions
    if "examples" in st.session_state:
        del st.session_state.examples


st.selectbox(
    "Select a table",
    options=configs.tables,
    index=None,
    label_visibility="collapsed",
    key="select",
    on_change=reset_dfs,
)
if st.session_state.select:

    if "descriptions" not in st.session_state:
        table_split = st.session_state.select.split(".")
        desc_query = f"""
        SELECT
          column_name AS `Column Name`, data_type AS `Data Type`, description AS Description
        FROM
          `{'.'.join(table_split[:-1])}`.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
        WHERE
          table_name = '{table_split[-1]}';
        """
        st.session_state.descriptions = bqm.execute_sql(desc_query)
    st.markdown("### Table description:")
    st.dataframe(st.session_state.descriptions)

    if "examples" not in st.session_state:
        eg_query = f"""
        SELECT
          *
        FROM
          `{st.session_state.select}`
        #PARTION_FILTER#
        LIMIT
          10;
        """
        eg_query = (
            eg_query.replace(
                "#PARTION_FILTER#", "WHERE\n  session_date > DATE_TRUNC(CURRENT_DATE(), MONTH)"
            )
            if "onlinebehaviour" in st.session_state.select
            else eg_query.replace("#PARTION_FILTER#", "")
        )
        st.session_state.examples = bqm.execute_sql(eg_query)
    st.markdown("### Example rows:")
    st.dataframe(st.session_state.examples)
