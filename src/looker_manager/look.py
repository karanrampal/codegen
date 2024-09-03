"""Looker Manager to extract explores, dimensions etc."""

import json
import os
from typing import Optional

import looker_sdk

from chat_manager.chatbot import ChatManager
from prompt_manager.task_prompts import TaskPrompts
from query_formatter.formatter import QueryFormatter
from secret_manager.secrets import SecretsManager


class LookerManager:
    """Class to extract data from lookerML"""

    def __init__(self, proj_id: str) -> None:
        self._init_looker(proj_id)
        self._looker_prompt = TaskPrompts()

    def _init_looker(self, proj_id: str) -> None:
        """Initialize looker"""
        sm = SecretsManager()
        os.environ["LOOKERSDK_CLIENT_ID"] = sm.get_secret(proj_id, "looker_sdk_client_id")
        os.environ["LOOKERSDK_CLIENT_SECRET"] = sm.get_secret(proj_id, "looker_sdk_client_secret")
        os.environ["LOOKERSDK_BASE_URL"] = "https://hmgroup.cloud.looker.com/"
        os.environ["LOOKERSDK_API_VERSION"] = "4.0"
        os.environ["LOOKERSDK_TIMEOUT"] = "120"
        self.sdk = looker_sdk.init40()

    def get_explores(self, lookml_model: str) -> list[Optional[str]]:
        """Gets a list of LookML explores for a given model

        Args:
            lookml_model (str): The name of the LookML model to use.

        Returns:
           explores: A list where each element is an explore name
        """
        response = self.sdk.all_lookml_models()
        explores = []
        for r in response:
            if r.name == lookml_model and r.explores:
                for e in r.explores:
                    explores.append(e.name)
                break
        return explores

    def get_dimensions_and_measures(
        self, lookml_model: str, lookml_explore: str
    ) -> tuple[list[dict[str, Optional[str]]], list[dict[str, Optional[str]]]]:
        """For a given model and explore, gets LookML dimensions and measures as dictionaries

        Args:
            lookml_model (str): The name of the LookML model to use.
            lookml_explore (str): The name of the LookML explore to use.

        Returns:
            dimensions, measures: The first element of the tuple is a list of dimension dictionary,
            the second is a list of measures dictionaries
        """
        # API Call to pull in metadata about fields in a particular explore
        explore = self.sdk.lookml_model_explore(
            lookml_model_name=lookml_model,
            explore_name=lookml_explore,
            fields="id, name, description, fields, label",
        )

        measures = []
        dimensions = []

        # Iterate through the dimensions and measures in the explore
        if explore.fields and explore.fields.dimensions:
            for dimension in explore.fields.dimensions:
                if not dimension.hidden:
                    def_dimension = {
                        "name": dimension.name,
                        "description": dimension.description,
                    }
                    dimensions.append(def_dimension)

        if explore.fields and explore.fields.measures:
            for measure in explore.fields.measures:
                if not measure.hidden:
                    def_measure = {
                        "name": measure.name,
                        "description": measure.description,
                    }
                    measures.append(def_measure)

        return dimensions, measures

    def get_explore_details_old(self, lookml_model: str) -> tuple[list, str]:
        """
        Gets a list of explore names under a model and a string description of all explores.

        Args:
            lookml_model (str): The name of the LookML model to use.

        Returns:
            explores, explore_def: The first element of the tuple is a list of explore names,
            the second is a string describing the explores.
        """
        explores = self.get_explores(lookml_model)
        explore_def = ""
        for e in explores:
            if not e:
                continue
            explore_details = self.sdk.lookml_model_explore(
                lookml_model_name=lookml_model,
                explore_name=e,
                fields="id, name, description, fields, label, joins",
            )

            # Display join details
            explore_def += f"explore: {e} {{\n"
            if explore_details.description:
                explore_def += f"  description: {explore_details.description}\n"
            if explore_details.joins:
                for join in explore_details.joins:
                    explore_def += (
                        f"  join: {join.name} {{\n    type: {join.type}\n    relationship: "
                        f"{join.relationship}\n    sql_on: {join.sql_on}\n  }}\n"
                    )

            explore_def += "}\n\n"

        return explores, explore_def

    def get_explore_details(self, lookml_model: str) -> tuple[list, list]:
        """Gets a list of explore names under a model and a string description of all explores.

        Args:
            lookml_model (str): The name of the LookML model to use.

        Returns:
            explores, explore_def: The first element of the tuple is a list of explore names,
            the second is a list of dictionaries describing the explores.
        """
        explores = self.get_explores(lookml_model)
        explore_def = []
        for e in explores:
            if not e:
                continue
            explore_details = self.sdk.lookml_model_explore(
                lookml_model_name=lookml_model,
                explore_name=e,
                fields="id, name, description, fields, label, joins",
            )
            desc = explore_details.description if explore_details.description else ""
            tjn = []
            if explore_details.joins:
                for join in explore_details.joins:
                    tjn.append(
                        {
                            "join": join.name,
                            "type": join.type,
                            "sql_on": join.sql_on,
                            "relationship": join.relationship,
                        }
                    )
            tmp = {"explore": e, "desciption": desc, "joins": tjn}
            explore_def.append(tmp)
        return explores, explore_def

    def get_looker_si(
        self,
        lookml_model: str,
    ) -> str:
        """Generates the system instruction for the chatbot to use
        Args:
            lookml_model (str): The name of the LookML model to use.

        Returns:
            looker prompt system instructions
        """
        explores, explore_def = self.get_explore_details(lookml_model)
        dimensions_dict, measures_dict = self.get_dimensions_and_measures(
            lookml_model, explores[0]
        )  # any one explore from the same model will do
        if not dimensions_dict:
            print("WARNING: no dimensions found")
        if not measures_dict:
            print("WARNING: no measures found")
        prompt_values = {
            "explore_details": json.dumps(explore_def),
            "dimensions": json.dumps(dimensions_dict),
            "measures": json.dumps(measures_dict),
        }
        return self._looker_prompt.looker_prompt(**prompt_values)

    def execute_llm_looker_query(self, llm: ChatManager, user_input: str, lookml_model: str) -> str:
        """Executes the logic to generate Looker visualization given a user's natural language query

        Args:
            llm (ChatManager): Chatbot model instance
            user_input (str): The user's natural language query or request.
            lookml_model (str): The name of the LookML model to use.
        Returns:
            html_string (str): The HTML string for an iframe that can be embedded in a webpage
        """
        if not user_input:
            return "<p>No input given</p>"
        try:
            explores = self.get_explores(lookml_model)
            model_ans = llm.get_chat_response(user_input)
            if "fields=" not in model_ans:
                return model_ans
            # print("Raw gemini response: ", model_ans)
            extracted_ans = QueryFormatter.extract_lookml_query_params(model_ans)
            extracted_fields = QueryFormatter.extract_lookml_query_fields_param(extracted_ans)
            explore_to_query = explores[0]
            for exp in explores:
                if exp and exp in extracted_fields:
                    explore_to_query = exp
                    break

            looker_base_url = (
                f"https://hmgroup.cloud.looker.com/embed/explore/{lookml_model}/{explore_to_query}?"
            )
            query_url = QueryFormatter.format_lookml_query(extracted_ans, looker_base_url)

            return query_url
        except Exception as exc:  # pylint: disable=broad-except
            error_message = str(exc)
            print(error_message)
            return f"<p>There was an error while querying Looker: {error_message}</p>"
