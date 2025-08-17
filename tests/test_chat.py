"""Tests for ClaudeChat."""

from unittest.mock import Mock, patch

from chat import ClaudeChat


class TestClaudeChat:
    """Test cases for ClaudeChat class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.mock_client = Mock()

    @patch("chat.Anthropic")
    def test_chat_initialization(self, mock_anthropic):
        """Test that ClaudeChat initializes correctly."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)

        # ClaudeChat doesn't store api_key, it passes it to Anthropic client
        assert chat.client == self.mock_client
        assert chat.model == "claude-3-haiku-20240307"
        assert chat.debug is False
        assert chat.messages == []
        mock_anthropic.assert_called_once_with(api_key=self.api_key)

    @patch("chat.Anthropic")
    def test_chat_custom_parameters(self, mock_anthropic):
        """Test ClaudeChat with custom parameters."""
        mock_anthropic.return_value = self.mock_client

        custom_model = "claude-3-opus-20240229"
        custom_prompt = "Custom system prompt"

        chat = ClaudeChat(
            api_key=self.api_key,
            model=custom_model,
            system_prompt=custom_prompt,
            debug=True,
        )

        assert chat.model == custom_model
        assert chat.system_prompt == custom_prompt
        assert chat.debug is True

    @patch("chat.Anthropic")
    @patch("chat.Path")
    def test_write_debug_log(self, mock_path, mock_anthropic):
        """Test debug logging functionality."""
        mock_anthropic.return_value = self.mock_client
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance

        chat = ClaudeChat(api_key=self.api_key, debug=True)
        chat.messages = [{"role": "user", "content": "test"}]

        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            chat._write_debug_log("test_debug.json")

            mock_path.assert_called_once_with("test_debug.json")
            mock_path_instance.parent.mkdir.assert_called_once_with(exist_ok=True)
            mock_open.assert_called_once_with("test_debug.json", "w")

    @patch("chat.Anthropic")
    def test_write_debug_log_disabled(self, mock_anthropic):
        """Test that debug logging is skipped when disabled."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)

        with patch("builtins.open", create=True) as mock_open:
            chat._write_debug_log()
            mock_open.assert_not_called()

    @patch("chat.Anthropic")
    def test_reset_conversation(self, mock_anthropic):
        """Test conversation reset functionality."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)
        chat.messages = [{"role": "user", "content": "test"}]

        chat.reset_conversation()

        assert chat.messages == []

    @patch("chat.Anthropic")
    def test_execute_tool_get_current_time(self, mock_anthropic):
        """Test executing get_current_time tool."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)
        result = chat._execute_tool("get_current_time", {})

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("chat.Anthropic")
    def test_execute_tool_unknown(self, mock_anthropic):
        """Test executing unknown tool."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)
        result = chat._execute_tool("unknown_tool", {})

        assert "Error: Unknown tool 'unknown_tool'" in result

    @patch("chat.Anthropic")
    def test_initialize_tools(self, mock_anthropic):
        """Test tool initialization."""
        mock_anthropic.return_value = self.mock_client

        chat = ClaudeChat(api_key=self.api_key, debug=False)
        tools = chat._initialize_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that get_current_time tool is included
        tool_names = [tool["name"] for tool in tools]
        assert "get_current_time" in tool_names
