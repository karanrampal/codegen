"""Class to manage Chatbot configs"""

import vertexai
from vertexai.generative_models import GenerativeModel


class ChatManager:  # pylint: disable=too-few-public-methods
    """Manage Chatbot config and api calls
    kwargs:
        temp (float): Model temperature
        max_tokens (int): Max output tokens
    """

    def __init__(
        self, proj_id: str, model_name: str, system_instruction: str, **kwargs: float | int
    ) -> None:
        model_params = {
            "temperature": kwargs.get("temp", 0.0),
            "candidate_count": 1,
            "max_output_tokens": kwargs.get("max_tokens", 1024),
        }
        vertexai.init(project=proj_id, location="europe-west1")
        self.system_instruction = system_instruction
        llm = GenerativeModel(
            model_name, system_instruction=self.system_instruction, generation_config=model_params
        )
        self.chat = llm.start_chat()

    def get_chat_response(self, text_prompt: str) -> str:
        """Get chat response"""
        responses = self.chat.send_message(text_prompt, stream=True)
        text_response = [chunk.text for chunk in responses]
        return "".join(text_response)
