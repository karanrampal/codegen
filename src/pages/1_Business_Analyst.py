# pylint: disable=invalid-name,duplicate-code
"""Streamlit app UI for Business Analysts"""

import streamlit as st
import streamlit.components.v1 as components

from chat_manager.chatbot import ChatManager
from config_manager.manager import Params
from looker_manager.look import LookerManager

st.set_page_config(page_title="Assistant", page_icon="⚡", layout="wide")

if "select" in st.session_state:
    st.session_state.select = st.session_state.select


@st.cache_resource
def init_setup_ba() -> tuple[ChatManager, LookerManager]:
    """Setup the page"""
    configs = Params("./configs/config.yml")
    lm_ = LookerManager(configs.project_id)
    return ChatManager(configs.project_id, configs.llm, lm_.get_looker_si("segment")), lm_


llm, looker_manager = init_setup_ba()

st.sidebar.markdown("# 🎈 Business Analyst")

st.markdown(
    """
    # 🎈 Business Analyst

    #### Start chatting below :+1:!
    """
)

if "response" not in st.session_state:
    st.session_state.response = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = looker_manager.execute_llm_looker_query(llm, prompt, "segment")
        if "https" in response:
            st.session_state.response = response
            response = f"[Checkout Explore]({response})"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if "https" in st.session_state.response:
    result = st.session_state.response
    components.iframe(result, height=600)
