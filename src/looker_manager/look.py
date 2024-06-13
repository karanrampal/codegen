"""Class to manage LLM configs"""

import vertexai
from vertexai.preview.generative_models import GenerativeModel


class LLMManager:  # pylint: disable=too-few-public-methods
    """Manage LLM config and api calls"""

    def __init__(
        self, proj_id: str, model_name: str, temp: float = 0.0, max_tokens: int = 1024
    ) -> None:
        model_params = {"temperature": temp, "candidate_count": 1, "max_output_tokens": max_tokens}
        vertexai.init(project=proj_id, location="europe-west1")
        self.llm = GenerativeModel(model_name, generation_config=model_params)

    def get_response(self, text_prompt: str) -> str:
        """Get LLM response"""
        response = self.llm.generate_content(
            contents=text_prompt,
        )
        return response.text
