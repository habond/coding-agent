#!/usr/bin/env python3

from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from anthropic import Anthropic
from anthropic.types import (
    Message,
    MessageParam,
    TextBlock,
    TextBlockParam,
    ToolParam,
    ToolResultBlockParam,
    ToolUseBlockParam,
)


if TYPE_CHECKING:
    from tools.registry import ToolRegistry


class ClaudeChat:
    """Manages conversations with Claude API including tool usage."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        system_prompt: str | None = None,
        debug: bool = True,
        tool_registry: "ToolRegistry | None" = None,
        tool_free: bool = False,
    ) -> None:
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = (
            system_prompt
            or "You are a helpful AI assistant. Be concise and clear in your responses."
        )
        self.messages: list[MessageParam] = []
        self.debug = debug
        self.tool_registry = tool_registry
        self.tool_free = tool_free
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> list[ToolParam]:
        """Initialize available tools."""
        if self.tool_registry:
            return self.tool_registry.get_tool_definitions()

        return [
            ToolParam(
                name="get_current_time",
                description="Get the current date and time",
                input_schema={"type": "object", "properties": {}, "required": []},
            )
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if self.tool_registry:
            return self.tool_registry.execute(tool_name, tool_input)

        if tool_name == "get_current_time":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return f"Error: Unknown tool '{tool_name}'"

    def _handle_tool_use(self, response: Message) -> tuple[str, str | None, str | None]:
        """Handle tool use in Claude's response."""
        tool_use = None
        assistant_content: list[TextBlockParam | ToolUseBlockParam] = []
        output_text = ""

        for content in response.content:
            if content.type == "text":
                assistant_content.append(TextBlockParam(type="text", text=content.text))
                if content.text:
                    output_text += content.text
            elif content.type == "tool_use":
                tool_use = content
                assistant_content.append(
                    ToolUseBlockParam(
                        type="tool_use",
                        id=tool_use.id,
                        name=tool_use.name,
                        input=cast(dict[str, Any], tool_use.input)
                        if tool_use.input
                        else {},
                    )
                )

        self.messages.append(MessageParam(role="assistant", content=assistant_content))

        if tool_use:
            tool_input = cast(dict[str, Any], tool_use.input) if tool_use.input else {}
            result = self._execute_tool(tool_use.name, tool_input)
            tool_display = f"[Tool: {tool_use.name} -> {result}]"

            self.messages.append(
                MessageParam(
                    role="user",
                    content=[
                        ToolResultBlockParam(
                            type="tool_result",
                            tool_use_id=tool_use.id,
                            content=result,
                        )
                    ],
                )
            )

            if self.tool_free:
                follow_up = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=self.system_prompt,
                    messages=self.messages,
                )
            else:
                follow_up = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=self.system_prompt,
                    messages=self.messages,
                    tools=self.tools,
                )

            follow_up_text = ""
            if follow_up.content and isinstance(follow_up.content[0], TextBlock):
                follow_up_text = follow_up.content[0].text
            self.messages.append(MessageParam(role="assistant", content=follow_up_text))

            return output_text, tool_display, follow_up_text

        return output_text, None, None

    def send_message(self, user_input: str) -> tuple[str, str | None]:
        """Send a message to Claude and get the response."""
        self.messages.append(MessageParam(role="user", content=user_input))

        if self.tool_free:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.messages,
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.messages,
                tools=self.tools,
            )

        if response.stop_reason == "tool_use":
            text, tool_display, follow_up = self._handle_tool_use(response)
            combined_text = ""
            if text and tool_display and follow_up:
                combined_text = text + "\n" + tool_display + "\n" + follow_up
            elif tool_display and follow_up:
                combined_text = tool_display + "\n" + follow_up
            return combined_text, tool_display
        else:
            assistant_message = ""
            if response.content and isinstance(response.content[0], TextBlock):
                assistant_message = response.content[0].text
            self.messages.append(
                MessageParam(role="assistant", content=assistant_message)
            )
            return assistant_message, None

    def reset_conversation(self) -> None:
        """Clear the conversation history."""
        self.messages = []
