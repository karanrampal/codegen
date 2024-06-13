"""Utility functions"""

import shutil
from glob import glob
from typing import Optional

import pandas as pd
from autoviz.AutoViz_Class import AutoViz_Class
from PIL import Image

from llm_manager.llm import LLMManager
from prompt_manager.task_prompts import TaskPrompts
from query_formatter.formatter import QueryFormatter


def get_proposed_query(
    question: str,
    llm: LLMManager,
    prompts: TaskPrompts,
    use_reflection: bool = True,
    **kwargs: str | int,
) -> str:
    """Query the LLM to generate SQL from natural language

    Args:
        question (str): The user's natural language query.
        llm (LLMManager): LLM to be used for prompting
        prompts (PromptManager): Taks prompt manager
        use_reflection (bool): Whether to use the reflection pattern. If true, the LLM will be
            called a second time with the second prompt in the prompt_chain tuple.

    Kwargs:
        schemas_and_rows (str): A descriptive unstructured text of the schemas and top-n rows from
            the tables.
        cols_descriptions (str): An optional but recommended unstructured string that includes
            column descriptions.
        dataset_info (str): An optional but recommended unstructured string that includes additional
            info about the data.
        num_rows (int): The number of sample rows the model is being presented with.

    Returns:
        The SQL query proposed by the LLM
    """
    if not question:
        return ""

    sql_text_prompt = prompts.sql_prompt(
        schemas_and_rows=kwargs["schemas_and_rows"],
        col_descriptions=kwargs["cols_descriptions"],
        additional_notes=kwargs["dataset_info"],
        num_rows=kwargs["num_rows"],
        question=question,
    )

    llm_response = llm.get_response(sql_text_prompt)
    extracted_query = QueryFormatter.extract_sql(llm_response)

    if use_reflection:
        reflect_llm_prompt = prompts.sql_reflection_prompt(
            schemas_and_rows=kwargs["schemas_and_rows"],
            additional_notes=kwargs["dataset_info"],
            answer=extracted_query,
            num_rows=kwargs["num_rows"],
            question=question,
        )

        reflect_llm_response = llm.get_response(reflect_llm_prompt)
        extracted_reflect_query = QueryFormatter.extract_sql(reflect_llm_response)

        return extracted_reflect_query

    return extracted_query


def merge_imgs(im1: Image.Image, im2: Image.Image) -> Image.Image:
    """Merge two images vertically"""
    h = im1.size[1] + im2.size[1]
    w = max(im1.size[0], im2.size[0])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (0, im1.size[1]))

    return im


def autogen_viz(data: pd.DataFrame) -> Optional[list[str]]:
    """Autogenerate visualizations"""
    if data is None:
        return None
    row, col = data.shape
    if row == 1 or col == 1:
        return None
    av_ = AutoViz_Class()
    shutil.rmtree("./data/AutoViz/", ignore_errors=True)
    try:
        av_.AutoViz(filename="", dfte=data, chart_format="jpg", verbose=2, save_plot_dir="./data/")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Couldn't create plots, check input data! {exc}")
    im_list = glob("./data/AutoViz/*.jpg")
    if not im_list:
        return None
    return im_list
