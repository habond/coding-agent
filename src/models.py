"""Type definitions for the Claude CLI application."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Protocol, TypedDict, cast

from anthropic.types import ToolParam


class ToolInputSchema(TypedDict):
    """Type definition for tool input JSON schema."""

    type: str
    properties: dict[str, dict[str, str]]
    required: list[str]


class ToolMetadata(TypedDict):
    """Type definition for tool metadata."""

    name: str
    description: str
    handler: Callable[[dict[str, Any]], str]
    input_schema: ToolInputSchema


class ToolExecutionResult(TypedDict):
    """Type definition for tool execution results."""

    success: bool
    result: str
    error: str | None


class ToolRegistryProtocol(Protocol):
    """Protocol defining the interface for tool registries."""

    @property
    def tools(self) -> dict[str, ToolMetadata]:
        """Get all registered tools."""
        ...

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable[[dict[str, Any]], str],
        input_schema: ToolInputSchema,
    ) -> None:
        """Register a new tool."""
        ...

    def get_tool_definitions(self) -> list[ToolParam]:
        """Get tool definitions for Claude API."""
        ...

    def execute(self, tool_name: str, tool_input: dict[str, Any] | None = None) -> str:
        """Execute a tool by name."""
        ...

    def list_tools(self) -> list[str]:
        """Get a list of all registered tool names."""
        ...


class AbstractToolRegistry(ABC):
    """Abstract base class for tool registries."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolMetadata] = {}

    @property
    def tools(self) -> dict[str, ToolMetadata]:
        """Get all registered tools."""
        return self._tools.copy()

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable[[dict[str, Any]], str],
        input_schema: ToolInputSchema,
    ) -> None:
        """Register a new tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            handler: The function to call when the tool is executed
            input_schema: JSON schema for the tool's input parameters
        """
        self._tools[name] = ToolMetadata(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
        )

    def get_tool_definitions(self) -> list[ToolParam]:
        """Get tool definitions for Claude API.

        Returns:
            List of tool definitions in the format expected by Claude API
        """
        return [
            ToolParam(
                name=tool["name"],
                description=tool["description"],
                input_schema=cast(dict[str, Any], tool["input_schema"]),
            )
            for tool in self._tools.values()
        ]

    def execute(self, tool_name: str, tool_input: dict[str, Any] | None = None) -> str:
        """Execute a tool by name.

        Args:
            tool_name: The name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            The result of the tool execution as a string
        """
        if tool_name not in self._tools:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            handler = self._tools[tool_name]["handler"]
            result = handler(tool_input or {})
            return str(result)  # Ensure we return a string
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def list_tools(self) -> list[str]:
        """Get a list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    @abstractmethod
    def load_tools(self) -> None:
        """Load tools into the registry. Implementation-specific."""
        pass
