# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Python CLI application for interacting with Claude AI through the Anthropic API. The application supports both interactive REPL mode and single-message execution, with an extensible tool system for adding custom capabilities.

## Development Commands

### Running the Application
```bash
# Interactive REPL mode
./run.sh

# Single message mode
./run.sh "Your message here"

# Using Python directly
python src/main.py
```

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chat.py

# Run tests with specific marker
pytest -m unit
```

### Code Quality
```bash
# Check code style and lint
ruff check

# Format code
ruff format

# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture

### Core Components

- **`src/main.py`**: Entry point with CLI argument parsing and application setup
- **`src/chat.py`**: `ClaudeChat` class that manages API communication, conversation state, and tool execution
- **`src/tools/registry.py`**: `ToolRegistry` class for dynamic tool loading and management
- **`src/tools/`**: Individual tool implementations with `TOOL_METADATA` for auto-registration

### Tool System
Tools are automatically loaded from the `src/tools/` directory. Each tool file must define:
- A handler function that takes `params: dict[str, Any]` and returns a string
- `TOOL_METADATA` dictionary with `name`, `description`, `handler`, and `input_schema`

### Configuration
The application uses `config.json` for settings including model selection, debug mode, and feature flags. Environment variables are loaded from `.env` file.

### Key Dependencies
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `pytest`: Testing framework
- `ruff`: Code linting and formatting
- `pre-commit`: Git hooks for code quality

### Testing Structure
Tests use pytest with mocking for external dependencies. The `conftest.py` sets up the Python path to import from `src/`. Test files follow the pattern `test_*.py` and are organized in the `tests/` directory.
