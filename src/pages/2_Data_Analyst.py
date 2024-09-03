# pylint: disable=invalid-name,duplicate-code
"""Streamlit app UI for Data Analysts"""

import streamlit as st
import streamlit.components.v1 as components

from bq_manager.query import BQManager
from chat_manager.chatbot import ChatManager
from config_manager.manager import Params
from prompt_manager.task_prompts import TaskPrompts
from query_formatter.formatter import QueryFormatter
from schema_manager.schema import SchemaManager
from utils.utils import get_proposed_query, visualize

st.set_page_config(page_title="Assistant", page_icon="⚡", layout="wide")

if "select" in st.session_state:
    st.session_state.select = st.session_state.select


@st.cache_resource
def init_setup_da() -> tuple[ChatManager, ChatManager, BQManager]:
    """Setup the page"""
    confs = Params("./configs/config.yml")
    sm_ = SchemaManager(confs)
    tp_ = TaskPrompts()

    s_prompt = tp_.sql_prompt(
        schemas_and_rows=sm_.get_schemas(),
        additional_notes=sm_.get_dataset_info(),
        num_rows=confs.num_rows,
    )
    r_prompt = tp_.sql_reflection_prompt(
        schemas_and_rows=sm_.get_schemas(),
        additional_notes=sm_.get_dataset_info(),
        num_rows=confs.num_rows,
    )
    sql_bot = ChatManager(confs.project_id, confs.llm, s_prompt)
    reflect_bot = ChatManager(confs.project_id, confs.llm, r_prompt)
    return (
        sql_bot,
        reflect_bot,
        BQManager(confs),
    )


sbot, rbot, bqm = init_setup_da()

st.sidebar.markdown("# ❄️ Data Analyst")

st.markdown(
    """
    # ❄️ Data Analyst

    #### Ask a question :+1:!
    """
)

if "messages_da" not in st.session_state:
    st.session_state.messages_da = []
for message in st.session_state.messages_da:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question?"):
    st.session_state.messages_da.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = get_proposed_query(prompt, sbot, rbot)
        if "SELECT" in response:
            fmt_query = QueryFormatter.format_query(response)
            result = bqm.execute_sql(fmt_query)
            st.session_state.df = result
            response = f"```{response}```\n{result.to_markdown()}"
            if len(result) > 1:
                html_data = visualize(sbot, result)
                components.html(html_data, height=450, scrolling=True)
        if "```python" in response and "df" in st.session_state:
            html_data = visualize(sbot, st.session_state.df, response)
            components.html(html_data, height=450, scrolling=True)

        st.markdown(response)
    st.session_state.messages_da.append({"role": "assistant", "content": response})
