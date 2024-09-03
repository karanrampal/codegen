"""Unit tests for ChatManager class"""

from unittest.mock import MagicMock, patch

from chat_manager.chatbot import ChatManager


@patch("vertexai.init")
def test_chat_manager_init(
    mock_init: MagicMock,
    proj_id: str = "test-project",
    model_name: str = "test-model",
    system_instruction: str = "Test instruction",
) -> None:
    """Test initialization"""
    chat_manager = ChatManager(proj_id, model_name, system_instruction)

    mock_init.assert_called_once_with(project=proj_id, location="europe-west1")
    assert chat_manager.system_instruction == system_instruction
    assert chat_manager.chat is not None


@patch("vertexai.generative_models.ChatSession.send_message")
def test_get_chat_response(mock_send_message: MagicMock, text_prompt: str = "Test prompt") -> None:
    """Test get_chat_response"""
    mock_responses = [MagicMock(text="Response part 1"), MagicMock(text="Response part 2")]
    mock_send_message.return_value = mock_responses

    chat_manager = ChatManager(
        proj_id="test-project", model_name="test-model", system_instruction="Test instruction"
    )

    response = chat_manager.get_chat_response(text_prompt)

    mock_send_message.assert_called_once_with(text_prompt, stream=True)

    assert response == "Response part 1Response part 2"
