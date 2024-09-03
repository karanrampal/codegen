"""Add unit tests for the llm manager module"""

from unittest.mock import MagicMock, patch

import pytest
from vertexai.generative_models import GenerativeModel

from llm_manager.llm import LLMManager


@patch("vertexai.init")
def test_llm_manager_init(
    mock_init: MagicMock, proj_id: str = "test-project", model_name: str = "text-davinci-003"
) -> None:
    """Test LLMManager initialization."""
    llm_manager = LLMManager(proj_id, model_name)

    mock_init.assert_called_once_with(project=proj_id, location="europe-west1")
    assert isinstance(llm_manager.llm, GenerativeModel)


@patch("vertexai.generative_models.GenerativeModel.generate_content")
def test_get_response(mock_generate_content: MagicMock, text_prompt: str = "Hello, world!") -> None:
    """Test get_response method."""
    mock_generate_content.return_value = MagicMock(text="This is a response.")

    llm_manager = LLMManager(proj_id="test-project", model_name="text-davinci-003")
    response = llm_manager.get_response(text_prompt)

    assert response == "This is a response."
    mock_generate_content.assert_called_once_with(contents=text_prompt)


@patch("vertexai.generative_models.GenerativeModel.generate_content")
def test_get_response_with_params(
    mock_generate_content: MagicMock, text_prompt: str = "Hello, world!"
) -> None:
    """Test get_response method with custom parameters."""
    mock_generate_content.return_value = MagicMock(text="This is a response with custom params.")
    llm_manager = LLMManager(
        proj_id="test-project", model_name="text-davinci-003", temp=0.5, max_tokens=2048
    )
    response = llm_manager.get_response(text_prompt)

    assert response == "This is a response with custom params."
    mock_generate_content.assert_called_once_with(contents=text_prompt)


def test_get_response_exception(text_prompt: str = "Hello, world!") -> None:
    """Test get_response method handling exceptions."""
    with patch(
        "vertexai.generative_models.GenerativeModel.generate_content",
        side_effect=Exception("Mock Error"),
    ):
        llm_manager = LLMManager(proj_id="test-project", model_name="text-davinci-003")
        with pytest.raises(Exception) as e:
            llm_manager.get_response(text_prompt)
        assert str(e.value) == "Mock Error"
