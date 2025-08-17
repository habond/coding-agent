"""Tests for ToolRegistry."""

from tools.registry import ToolRegistry


class TestToolRegistry:
    """Test cases for ToolRegistry."""

    def test_registry_initialization(self):
        """Test that ToolRegistry initializes correctly."""
        registry = ToolRegistry(auto_load=False)
        assert isinstance(registry.tools, dict)
        assert len(registry.tools) == 0

    def test_auto_load_tools(self):
        """Test that auto-loading finds and loads tools."""
        registry = ToolRegistry(auto_load=True)
        assert len(registry.tools) > 0
        assert "read_file" in registry.tools
        assert "write_file" in registry.tools

    def test_register_tool(self):
        """Test manual tool registration."""
        registry = ToolRegistry(auto_load=False)

        def dummy_tool(params):
            return "dummy result"

        registry.register_tool(
            name="test_tool",
            description="A test tool",
            handler=dummy_tool,
            input_schema={"type": "object", "properties": {}, "required": []},
        )

        assert "test_tool" in registry.tools
        assert registry.tools["test_tool"]["handler"] == dummy_tool

    def test_get_tool_definitions(self):
        """Test getting tool definitions for Claude API."""
        registry = ToolRegistry(auto_load=True)
        definitions = registry.get_tool_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) > 0

        # Check structure of first definition
        tool_def = definitions[0]
        assert "name" in tool_def
        assert "description" in tool_def
        assert "input_schema" in tool_def
        assert "handler" not in tool_def  # Should not include handler in API definition

    def test_execute_existing_tool(self):
        """Test executing an existing tool."""
        registry = ToolRegistry(auto_load=True)
        result = registry.execute(
            "read_file", {"file_path": "/app/sandbox/nonexistent.txt"}
        )
        assert isinstance(result, str)
        assert "Error:" in result

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        registry = ToolRegistry(auto_load=False)
        result = registry.execute("nonexistent_tool")
        assert "Error: Unknown tool 'nonexistent_tool'" in result

    def test_execute_with_parameters(self):
        """Test executing a tool with parameters."""
        registry = ToolRegistry(auto_load=True)
        # Test read_file with a file that doesn't exist (will return error)
        result = registry.execute(
            "read_file", {"file_path": "/app/sandbox/nonexistent.txt"}
        )
        assert "Error:" in result

    def test_execute_with_error(self):
        """Test error handling during tool execution."""
        registry = ToolRegistry(auto_load=False)

        def error_tool(params):
            raise ValueError("Test error")

        registry.register_tool(
            name="error_tool",
            description="A tool that errors",
            handler=error_tool,
            input_schema={"type": "object", "properties": {}, "required": []},
        )

        result = registry.execute("error_tool")
        assert "Error executing error_tool: Test error" in result

    def test_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry(auto_load=True)
        tools = registry.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "read_file" in tools
        assert "write_file" in tools
