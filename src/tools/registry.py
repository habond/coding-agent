"""Tool registry for managing available tools."""

import importlib
from pathlib import Path
from typing import Any

from models import AbstractToolRegistry, ToolInputSchema, ToolMetadata


class ToolRegistry(AbstractToolRegistry):
    """Registry for managing available tools."""

    def __init__(self, auto_load: bool = True) -> None:
        """Initialize the tool registry.

        Args:
            auto_load: Whether to automatically load all tools from the tools directory
        """
        super().__init__()
        if auto_load:
            self.load_tools()

    def load_tools(self) -> None:
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
                    metadata: ToolMetadata = module.TOOL_METADATA
                    self.register_tool(
                        name=metadata["name"],
                        description=metadata["description"],
                        handler=metadata["handler"],
                        input_schema=metadata["input_schema"],
                    )
            except Exception as e:
                print(f"Warning: Could not load tool from {tool_file}: {e}")

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Any,  # Keep as Any for compatibility with existing tools
        input_schema: ToolInputSchema,
    ) -> None:
        """Register a new tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            handler: The function to call when the tool is executed
            input_schema: JSON schema for the tool's input parameters
        """
        super().register_tool(name, description, handler, input_schema)
