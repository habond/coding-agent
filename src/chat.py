#!/usr/bin/env python3

from collections.abc import Generator
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
        tool_registry: "ToolRegistry | None" = None,
    ) -> None:
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = (
            system_prompt
            or "You are a helpful AI assistant. Be concise and clear in your responses."
        )
        self.messages: list[MessageParam] = []
        self.tool_registry = tool_registry
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> list[ToolParam]:
        """Initialize available tools."""
        if self.tool_registry:
            return self.tool_registry.get_tool_definitions()

        # No fallback tools - use ToolRegistry
        from tools.registry import ToolRegistry

        registry = ToolRegistry(auto_load=True)
        return registry.get_tool_definitions()

    def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if self.tool_registry:
            return self.tool_registry.execute(tool_name, tool_input)

        # No fallback execution - use ToolRegistry
        from tools.registry import ToolRegistry

        registry = ToolRegistry(auto_load=True)
        return registry.execute(tool_name, tool_input)

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

            follow_up = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.messages,
                tools=self.tools,
            )

            # Check if follow-up response also contains tool use
            if follow_up.stop_reason == "tool_use":
                # Recursively handle additional tool use
                follow_up_text, follow_up_tool_display, final_text = (
                    self._handle_tool_use(follow_up)
                )
                combined_follow_up = ""
                if follow_up_text and follow_up_tool_display and final_text:
                    combined_follow_up = (
                        follow_up_text
                        + "\n"
                        + follow_up_tool_display
                        + "\n"
                        + final_text
                    )
                elif follow_up_tool_display and final_text:
                    combined_follow_up = follow_up_tool_display + "\n" + final_text
                elif final_text:
                    combined_follow_up = final_text
                return output_text, tool_display, combined_follow_up
            else:
                follow_up_text = ""
                if follow_up.content and isinstance(follow_up.content[0], TextBlock):
                    follow_up_text = follow_up.content[0].text
                self.messages.append(
                    MessageParam(role="assistant", content=follow_up_text)
                )
                return output_text, tool_display, follow_up_text

        return output_text, None, None

    def send_message(self, user_input: str) -> tuple[str, str | None]:
        """Send a message to Claude and get the response."""
        self.messages.append(MessageParam(role="user", content=user_input))

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

    def _handle_tool_use_stream(
        self, response: Message
    ) -> Generator[tuple[str, str | None, bool], None, None]:
        """Handle tool use in Claude's response with streaming."""
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
            yield (
                "\n\n"
                + "=" * 40
                + "\n[TOOL CALL]\n"
                + "=" * 40
                + "\n\n"
                + tool_display,
                tool_display,
                False,
            )

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

            # Stream the follow-up response
            yield (
                "\n\n" + "=" * 40 + "\n[ASSISTANT MESSAGE]\n" + "=" * 40 + "\n\n",
                None,
                False,
            )
            with self.client.messages.stream(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.messages,
                tools=self.tools,
            ) as follow_stream:
                follow_accumulated = ""

                for event in follow_stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            text_chunk = event.delta.text
                            follow_accumulated += text_chunk
                            yield (text_chunk, None, False)

                follow_message = follow_stream.get_final_message()

                # Check if follow-up also has tool use
                if follow_message.stop_reason == "tool_use":
                    # Recursively handle additional tool use with streaming
                    yield from self._handle_tool_use_stream(follow_message)
                else:
                    # Store the follow-up message
                    self.messages.append(
                        MessageParam(role="assistant", content=follow_accumulated)
                    )
                    yield ("", None, True)
        else:
            yield ("", None, True)

    def send_message_stream(
        self, user_input: str
    ) -> Generator[tuple[str, str | None, bool], None, None]:
        """Send a message and stream the response.

        Yields tuples of (text_chunk, tool_info, is_complete)
        """
        self.messages.append(MessageParam(role="user", content=user_input))

        with self.client.messages.stream(
            model=self.model,
            max_tokens=1000,
            system=self.system_prompt,
            messages=self.messages,
            tools=self.tools,
        ) as stream:
            accumulated_text = ""
            tool_calls = []

            for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        text_chunk = event.delta.text
                        accumulated_text += text_chunk
                        yield (text_chunk, None, False)
                elif event.type == "content_block_stop":
                    if (
                        hasattr(event, "content_block")
                        and event.content_block.type == "tool_use"
                    ):
                        tool_calls.append(event.content_block)

            # Get the final message from stream
            final_message = stream.get_final_message()

            # Handle tool use if present
            if final_message.stop_reason == "tool_use":
                # Use streaming tool handler
                yield from self._handle_tool_use_stream(final_message)
            else:
                # Store the final assistant message
                self.messages.append(
                    MessageParam(role="assistant", content=accumulated_text)
                )
                yield ("", None, True)

    def reset_conversation(self) -> None:
        """Clear the conversation history."""
        self.messages = []
