#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from anthropic import Anthropic


class ClaudeChat:
    """Manages conversations with Claude API including tool usage."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        system_prompt: str | None = None,
        debug: bool = True,
    ):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = (
            system_prompt
            or "You are a helpful AI assistant. Be concise and clear in your responses."
        )
        self.messages: list[dict[str, Any]] = []
        self.debug = debug
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> list[dict[str, Any]]:
        """Initialize available tools."""
        return [
            {
                "name": "get_current_time",
                "description": "Get the current date and time",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if tool_name == "get_current_time":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return f"Error: Unknown tool '{tool_name}'"

    def _write_debug_log(self, filename: str = "logs/debug.json"):
        """Write conversation history to debug file."""
        if self.debug:
            # Create logs directory if it doesn't exist
            log_path = Path(filename)
            log_path.parent.mkdir(exist_ok=True)

            with open(filename, "w") as f:
                json.dump(self.messages, f, indent=2)

    def _handle_tool_use(self, response):
        """Handle tool use in Claude's response."""
        tool_use = None
        assistant_content = []
        output_text = ""

        for content in response.content:
            if content.type == "text":
                assistant_content.append({"type": "text", "text": content.text})
                if content.text:
                    output_text += content.text
            elif content.type == "tool_use":
                tool_use = content
                assistant_content.append(
                    {
                        "type": "tool_use",
                        "id": tool_use.id,
                        "name": tool_use.name,
                        "input": tool_use.input,
                    }
                )

        self.messages.append({"role": "assistant", "content": assistant_content})
        self._write_debug_log()

        if tool_use:
            result = self._execute_tool(tool_use.name, tool_use.input)
            tool_display = f"[Tool: {tool_use.name} -> {result}]"

            self.messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result,
                        }
                    ],
                }
            )
            self._write_debug_log()

            follow_up = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.messages,
                tools=self.tools,
            )

            follow_up_text = follow_up.content[0].text if follow_up.content else ""
            self.messages.append({"role": "assistant", "content": follow_up_text})
            self._write_debug_log()

            return output_text, tool_display, follow_up_text

        return output_text, None, None

    def send_message(self, user_input: str) -> tuple[str, str | None]:
        """Send a message to Claude and get the response."""
        self.messages.append({"role": "user", "content": user_input})
        self._write_debug_log()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self.system_prompt,
            messages=self.messages,
            tools=self.tools,
        )

        if response.stop_reason == "tool_use":
            text, tool_display, follow_up = self._handle_tool_use(response)
            return (
                text + "\n" + tool_display + "\n" + follow_up
                if text
                else tool_display + "\n" + follow_up
            ), tool_display
        else:
            assistant_message = response.content[0].text
            self.messages.append({"role": "assistant", "content": assistant_message})
            self._write_debug_log()
            return assistant_message, None

    def reset_conversation(self):
        """Clear the conversation history."""
        self.messages = []
        self._write_debug_log()
