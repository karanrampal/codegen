#!/usr/bin/env python3
"""Application for SQL generation"""

import argparse
from functools import partial
from typing import Callable, Union

import gradio as gr
import pandas as pd

from bq_manager.query import BQManager
from config_manager.manager import Params
from llm_manager.llm import LLMManager
from looker_manager.look import LookerManager
from prompt_manager.task_prompts import TaskPrompts
from query_formatter.formatter import QueryFormatter
from schema_manager.schema import SchemaManager
from utils.utils import autogen_viz, get_proposed_query


def args_parser() -> argparse.Namespace:
    """Parse CLI arguments"""
    parser = argparse.ArgumentParser(prog="SQLGen", description="CLI argument parser")
    parser.add_argument("--run-local", action="store_true", help="Run locally")
    parser.add_argument(
        "--config", type=str, default="./configs/config.yml", help="Config location"
    )
    return parser.parse_args()


def main() -> None:  # pylint: disable=too-many-statements,too-many-locals
    """Main function"""
    args = args_parser()
    configs = Params(args.config)

    llm = LLMManager(configs.project_id, configs.llm)
    prompts = TaskPrompts()
    scm = SchemaManager(configs)
    proposed = partial(
        get_proposed_query,
        llm=llm,
        prompts=prompts,
        schemas_and_rows=scm.get_schemas(),
        cols_descriptions=scm.get_column_descriptions(),
        dataset_info=scm.get_dataset_info(),
        num_rows=configs.num_rows,
    )

    bqm = BQManager(configs)

    looker_manager = LookerManager(configs.project_id)

    with gr.Blocks(title="Analytical Assistant") as demo:
        gr.Markdown(
            """
            # Analytical Assistant!
            Type in a question below to generate the SQL and then execute it.
            """
        )

        # Generate Looker
        with gr.Tab("Looker Assistant"):
            with gr.Row():
                with gr.Column(scale=4):
                    look_ques_tb = gr.Textbox(label="Ask question")
                with gr.Column(scale=1):
                    look_gen_btn = gr.Button("Explore")

            with gr.Row():
                with gr.Column(scale=4):
                    embed_chart = gr.HTML(label="Looker_viz")

        def explore(input_: str) -> str:
            """Explore button click event listener"""
            return looker_manager.execute_llm_looker_query(llm, input_, "segment")

        _ = look_gen_btn.click(
            fn=explore,
            inputs=look_ques_tb,
            outputs=embed_chart,
        )

        # Generate SQL
        with gr.Tab("BQ Assistant"):
            with gr.Row():
                with gr.Column(scale=4):
                    ques_tb = gr.Textbox(label="Ask question")
                with gr.Column(scale=1):
                    gen_btn = gr.Button("Generate")

            with gr.Row():
                with gr.Column(scale=4):
                    gen_sql_tb = gr.Textbox(label="Generated SQL")
                with gr.Column(scale=1):
                    exe_btn = gr.Button("Execute")
                    cancel_btn = gr.Button("Cancel")

            with gr.Row(visible=False) as result_row:
                with gr.Column(scale=4):
                    res_df = gr.Dataframe(label="Result")
                with gr.Column(scale=1):
                    viz_btn = gr.Button("Visualize")

            with gr.Row(visible=False) as visualization_row:
                res_viz = gr.Gallery(preview=True, label="Visualization")

        def execute(query: str) -> dict[str, Union[gr.Row, Callable]]:
            """Execute button click event listener"""
            fmt_query = QueryFormatter.format_query(query)
            return {result_row: gr.Row(visible=True), res_df: bqm.execute_sql(fmt_query)}

        def visualize(res_df: pd.DataFrame) -> dict[str, Union[gr.Row, Callable]]:
            return {visualization_row: gr.Row(visible=True), res_viz: autogen_viz(res_df)}

        gen_btn.click(fn=proposed, inputs=ques_tb, outputs=gen_sql_tb, api_name="generate")
        exe_event = exe_btn.click(fn=execute, inputs=gen_sql_tb, outputs=[result_row, res_df])
        cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[exe_event])
        viz_btn.click(fn=visualize, inputs=res_df, outputs=[visualization_row, res_viz])

        # Data profiling
        with gr.Tab("Data Quality"):
            dp_btn = gr.Dropdown(choices=configs.tables, label="Data Profiling")
            html_component = gr.HTML()
        dp_btn.select(fn=bqm.data_profiling, inputs=dp_btn, outputs=html_component)

    if args.run_local:
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)
    demo.close()


if __name__ == "__main__":
    main()
