"""Utility functions"""

import io
import logging
from typing import Optional

import pandas as pd

from chat_manager.chatbot import ChatManager
from query_formatter.formatter import QueryFormatter


def get_proposed_query(
    question: str,
    sql_bot: ChatManager,
    reflect_bot: ChatManager,
    use_reflection: bool = True,
) -> str:
    """Query the LLM to generate SQL from natural language

    Args:
        question (str): The user's natural language query.
        sql_bot (ChatManager): LLM to be used for prompting
        reflect_bot (ChatManager): LLM to be used for reflection
        use_reflection (bool): Whether to use the reflection pattern. If true, the LLM will be
            called a second time with the second prompt in the prompt_chain tuple.

    Returns:
        The SQL query proposed by the LLM
    """
    if not question:
        return ""

    llm_response = sql_bot.get_chat_response(question)
    if "```sql" not in llm_response and "```googlesql" not in llm_response:
        return llm_response
    extracted_query = QueryFormatter.extract_sql(llm_response)

    if use_reflection:
        tmp = f"##Question:\n{question}\n\n##SQL query:{extracted_query}"
        reflect_llm_response = reflect_bot.get_chat_response(tmp)
        extracted_query = QueryFormatter.extract_sql(reflect_llm_response)

    return extracted_query


def set_logger(log_path: Optional[str] = None) -> None:
    """Set the logger to log info in terminal and file at log_path.
    Args:
        log_path: (string) location of log file
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s: %(message)s"))
        logger.addHandler(stream_handler)

        if log_path:
            file_handler = logging.FileHandler(log_path, mode="w")
            file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s: %(message)s"))
            logger.addHandler(file_handler)


def visualize(sbot: ChatManager, data: pd.DataFrame, response: Optional[str] = None) -> str:
    """Visualize input dataframe"""
    if not response:
        buffer = io.StringIO()
        data.info(memory_usage=False, buf=buffer)
        tmp = buffer.getvalue()
        ques = (
            "Write python code to make an interactive plot for the dataframe `data` using plotly "
            "express python package and save as html file called `result.html`. The dataframe has "
            f"the following info,\n\n{tmp}"
        )
        response = sbot.get_chat_response(ques)
    py_res = QueryFormatter.extract_python(response)
    exec(py_res, {}, {"data": data})  # pylint: disable=exec-used
    with open("result.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    return html_data
