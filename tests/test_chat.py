"""Tests for ClaudeChat."""

from typing import Any
from unittest.mock import Mock, patch

from anthropic.types import TextBlock

from chat import ClaudeChat


class TestClaudeChat:
    """Test cases for ClaudeChat class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.mock_client = Mock()

    @patch("chat.Anthropic")
    def test_chat_initialization(self, mock_anthropic: Any) -> None:
        """Test that ClaudeChat initializes correctly."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key)

        # ClaudeChat doesn't store api_key, it passes it to Anthropic client
        assert chat.client == self.mock_client
        assert chat.model == "claude-3-haiku-20240307"
        assert chat.messages == []
        mock_anthropic.assert_called_once_with(api_key=self.api_key)

    @patch("chat.Anthropic")
    def test_chat_custom_parameters(self, mock_anthropic: Any) -> None:
        """Test ClaudeChat with custom parameters."""
        mock_anthropic.return_value = self.mock_client

        custom_model = "claude-3-opus-20240229"
        custom_prompt = "Custom system prompt"

        chat = ClaudeChat(
            api_key=self.api_key,
            model=custom_model,
            system_prompt=custom_prompt,
        )

        assert chat.model == custom_model
        assert chat.system_prompt == custom_prompt

    @patch("chat.Anthropic")
    def test_reset_conversation(self, mock_anthropic: Any) -> None:
        """Test conversation reset functionality."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key)
        chat.messages = [{"role": "user", "content": "test"}]

        chat.reset_conversation()

        assert chat.messages == []

    @patch("chat.Anthropic")
    def test_execute_tool_get_current_time(self, mock_anthropic: Any) -> None:
        """Test executing get_current_time tool."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key)
        result = chat._execute_tool("get_current_time", {})

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("chat.Anthropic")
    def test_execute_tool_unknown(self, mock_anthropic: Any) -> None:
        """Test executing unknown tool."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key)
        result = chat._execute_tool("unknown_tool", {})

        assert "Error: Unknown tool 'unknown_tool'" in result

    @patch("chat.Anthropic")
    def test_initialize_tools(self, mock_anthropic: Any) -> None:
        """Test tool initialization."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key)
        tools = chat._initialize_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that get_current_time tool is included
        tool_names = [tool["name"] for tool in tools]
        assert "get_current_time" in tool_names

    @patch("chat.Anthropic")
    def test_send_message_no_tools(self, mock_anthropic: Any) -> None:
        """Test sending a message without tool use (mocked API)."""
        mock_anthropic.return_value = self.mock_client

        # Mock the API response
        mock_response = Mock()
        mock_content = Mock(spec=TextBlock)
        mock_content.text = "Hello! I'm Claude."
        mock_content.type = "text"
        mock_response.content = [mock_content]
        mock_response.stop_reason = "end_turn"
        self.mock_client.messages.create.return_value = mock_response

        chat = ClaudeChat(api_key=self.api_key)
        response, tool_info = chat.send_message("Hello")

        # Verify the API was called with mocked client
        self.mock_client.messages.create.assert_called_once()
        assert response == "Hello! I'm Claude."
        assert tool_info is None

        # Verify no real API key was used
        call_args = self.mock_client.messages.create.call_args
        assert "ANTHROPIC_API_KEY" not in str(call_args)

    @patch("chat.Anthropic")
    def test_send_message_with_tool_use(self, mock_anthropic: Any) -> None:
        """Test sending a message with tool use (mocked API)."""
        mock_anthropic.return_value = self.mock_client

        # Mock the initial tool use response
        mock_tool_content = Mock()
        mock_tool_content.type = "tool_use"
        mock_tool_content.id = "tool_123"
        mock_tool_content.name = "get_current_time"
        mock_tool_content.input = {}

        mock_response = Mock()
        mock_response.content = [mock_tool_content]
        mock_response.stop_reason = "tool_use"

        # Mock the follow-up response after tool execution
        mock_followup = Mock()
        mock_followup.content = [Mock(text="The current time is displayed above.")]

        self.mock_client.messages.create.side_effect = [mock_response, mock_followup]

        chat = ClaudeChat(api_key=self.api_key)
        response, tool_info = chat.send_message("What time is it?")

        # Verify the API was called twice (initial + follow-up)
        assert self.mock_client.messages.create.call_count == 2
        assert tool_info is not None
        assert "get_current_time" in tool_info

        # Verify no real API key was used
        for call in self.mock_client.messages.create.call_args_list:
            assert "ANTHROPIC_API_KEY" not in str(call)
