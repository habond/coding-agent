#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from chat import ClaudeChat
from tools import ToolRegistry


class ClaudeCLI:
    """Main CLI application for Claude chat."""

    def __init__(self, config_path: str = "config.json") -> None:
        load_dotenv()
        self.config = self._load_config(config_path)
        self.api_key = self._get_api_key()
        self.chat: ClaudeChat | None = None
        self.tool_registry: ToolRegistry | None = None

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load configuration from JSON file."""
        if Path(config_path).exists():
            with open(config_path, encoding="utf-8") as f:
                config: dict[str, Any] = json.load(f)
                return config
        return {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "system_prompt": "You are a helpful AI assistant.",
        }

    def _get_api_key(self) -> str:
        """Get API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables")
            print("Please set it in your .env file or as an environment variable")
            sys.exit(1)
        return api_key

    def _setup_chat(self) -> None:
        """Initialize chat with configuration."""
        # Setup tools
        self.tool_registry = ToolRegistry()

        # Create chat instance with tool registry
        self.chat = ClaudeChat(
            api_key=self.api_key,
            model=self.config.get("model", "claude-3-haiku-20240307"),
            system_prompt=self.config.get("system_prompt"),
            tool_registry=self.tool_registry,
        )

    def run_repl(self) -> None:
        """Run interactive REPL mode."""
        self._setup_chat()
        assert self.chat is not None

        print("Claude REPL - Interactive Mode")
        print("Type 'exit', 'quit', or 'q' to exit")
        print("Type 'reset' to clear conversation history")
        if self.tool_registry:
            tools_list = ", ".join(self.tool_registry.tools.keys())
            print(f"Tools available: {tools_list}")
        print("-" * 40)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "reset":
                    self.chat.reset_conversation()
                    print("Conversation history cleared.")
                    continue

                if not user_input:
                    continue

                response, tool_info = self.chat.send_message(user_input)

                if tool_info:
                    print(f"\n{tool_info}")
                print(f"\nClaude: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback

                traceback.print_exc()

    def run_single(self, message: str) -> None:
        """Run a single message and exit."""
        self._setup_chat()
        assert self.chat is not None

        try:
            response, tool_info = self.chat.send_message(message)
            if tool_info:
                print(tool_info)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Claude CLI - Chat with Claude AI")
    parser.add_argument(
        "message", nargs="?", help="Single message to send (non-interactive mode)"
    )
    parser.add_argument(
        "--config", default="config.json", help="Path to configuration file"
    )
    parser.add_argument("--model", help="Override model from config")

    args = parser.parse_args()

    cli = ClaudeCLI(config_path=args.config)

    # Override config with command-line arguments
    if args.model:
        cli.config["model"] = args.model

    if args.message:
        cli.run_single(args.message)
    else:
        cli.run_repl()


if __name__ == "__main__":
    main()
