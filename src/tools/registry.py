"""Tool registry for managing available tools."""

import importlib
from pathlib import Path
from typing import Any


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self, auto_load: bool = True):
        """Initialize the tool registry.

        Args:
            auto_load: Whether to automatically load all tools from the tools directory
        """
        self.tools = {}
        if auto_load:
            self._auto_load_tools()

    def _auto_load_tools(self):
        """Automatically load all tools from the tools directory."""
        tools_dir = Path(__file__).parent

        # Find all Python files in the tools directory (except __init__ and registry)
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.stem in ["__init__", "registry"]:
                continue

            try:
                # Import the module dynamically
                module_name = f"tools.{tool_file.stem}"
                module = importlib.import_module(module_name)

                # Check if the module has TOOL_METADATA
                if hasattr(module, "TOOL_METADATA"):
                    metadata = module.TOOL_METADATA
                    self.register_tool(
                        name=metadata["name"],
                        description=metadata["description"],
                        handler=metadata["handler"],
                        input_schema=metadata["input_schema"],
                    )
            except Exception as e:
                print(f"Warning: Could not load tool from {tool_file}: {e}")

    def register_tool(
        self, name: str, description: str, handler, input_schema: dict[str, Any]
    ):
        """Register a new tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            handler: The function to call when the tool is executed
            input_schema: JSON schema for the tool's input parameters
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "input_schema": input_schema,
        }

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get tool definitions for Claude API.

        Returns:
            List of tool definitions in the format expected by Claude API
        """
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"],
            }
            for tool in self.tools.values()
        ]

    def execute(self, tool_name: str, tool_input: dict[str, Any] = None) -> str:
        """Execute a tool by name.

        Args:
            tool_name: The name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            The result of the tool execution as a string
        """
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            handler = self.tools[tool_name]["handler"]
            return handler(tool_input or {})
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def list_tools(self) -> list[str]:
        """Get a list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())
