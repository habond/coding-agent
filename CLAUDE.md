# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Python CLI application for interacting with Claude AI through the Anthropic API. Features interactive REPL mode and single-message execution with real-time streaming output. Includes an extensible tool system for custom capabilities with secure sandbox file operations.

## Prerequisites & Setup

### Environment Configuration
Create `.env` file with your API key:
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### Virtual Environment Setup (for local development)
```bash
# Create virtual environment (both .venv and venv are gitignored)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Development Commands

### Running the Application

#### Docker Mode (Recommended - Secure)
```bash
# Interactive REPL mode
./run.sh

# Single message mode
./run.sh "Your message here"

# With docker-compose directly
docker compose run --rm claude-cli
docker compose run --rm claude-cli python src/main.py "Your message"

# Development shell access
docker compose run --rm claude-cli-dev
```

#### Local Mode
```bash
# Interactive REPL mode
./run.sh --local

# Single message mode
./run.sh --local "Your message here"

# Direct Python execution
python src/main.py
python src/main.py "Your message"
```

### Testing

```bash
# Run all tests (API-safe, automatically mocked)
pytest

# Run specific test file
pytest tests/test_chat.py

# Run single test
pytest tests/test_chat.py::TestClaudeChat::test_send_message_no_tools -v

# Run with verbose output
pytest -v

# Docker testing
docker compose run --rm claude-cli pytest
docker compose run --rm claude-cli pytest tests/test_chat.py -v
```

**Important**: All tests use automatic API mocking via `tests/conftest.py` - no real API calls or charges.

### Code Quality

```bash
# Run all pre-commit hooks (recommended before committing)
pre-commit run --all-files

# Individual checks:
ruff check --fix    # Lint and auto-fix
ruff format        # Format code
mypy src/          # Type check

# Docker equivalents:
docker compose run --rm claude-cli ruff check
docker compose run --rm claude-cli ruff format
docker compose run --rm claude-cli mypy src/
```

## Architecture

### Core Components

- **`src/main.py`**: Entry point, CLI parsing, conversation boundaries
- **`src/chat.py`**: `ClaudeChat` class managing API, streaming, tools
- **`src/models.py`**: Type definitions (`ToolMetadata`, `ToolRegistryProtocol`, etc.)
- **`src/tools/registry.py`**: Dynamic tool loading and management
- **`src/tools/*.py`**: Individual tool implementations

### Streaming Implementation

The streaming system provides real-time output:
- `send_message_stream()`: Yields text chunks as they arrive
- `_handle_tool_use_stream()`: Maintains streaming during tool execution
- Visual boundaries: `========` (40 chars) with labels [USER MESSAGE], [ASSISTANT MESSAGE], [TOOL CALL]
- Conversation state stored in `self.messages` for continuity

### Tool System

Tools auto-load from `src/tools/` directory. Each tool requires:
- Handler function: `params: dict[str, Any] -> str`
- `TOOL_METADATA`: TypedDict with `name`, `description`, `handler`, `input_schema`

#### Available Tools

**File Operations:**
- `read_file`: Read files in sandbox
- `write_file`: Write/append files (modes: 'w', 'a')
- `edit_file`: Find/replace text (replace_all option)
- `list_files`: List directory contents
- `rename_file`: Rename/move files
- `move_file`: Move files between directories with optional rename
- `delete_file`: Delete files

**Directory Operations:**
- `create_directory`: Create directories (with parents)
- `rename_directory`: Rename/move directories
- `delete_directory`: Delete directories (force option for non-empty)

#### Sandbox Security
- Path: `/app/sandbox` in Docker, `./sandbox` locally
- All file operations restricted to sandbox
- Path validation prevents directory traversal
- Auto-creates parent directories where appropriate

### Creating Custom Tools

```python
from typing import Any
from models import ToolMetadata

def my_tool(params: dict[str, Any]) -> str:
    """Tool implementation."""
    # Validate params
    if "required_param" not in params:
        return "Error: required_param is required"

    # Tool logic here
    return "Success: Tool executed"

TOOL_METADATA: ToolMetadata = {
    "name": "my_tool",
    "description": "What the tool does",
    "handler": my_tool,
    "input_schema": {
        "type": "object",
        "properties": {
            "required_param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["required_param"]
    }
}
```

## Testing Patterns

### Mocking OS Operations
```python
@patch("os.path.exists")
@patch("os.path.isfile")
@patch("os.makedirs")
def test_file_operation(self, mock_makedirs, mock_isfile, mock_exists):
    mock_exists.return_value = True
    mock_isfile.return_value = True

    result = your_function(params)
    self.assertIn("Success", result)
```

### Key Testing Notes
- Mock all OS operations for CI compatibility
- Test both success and error paths
- Use type annotations matching implementation
- `tests/conftest.py` automatically mocks Anthropic API

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`):
- Python 3.11, 3.12 testing
- ruff linting/formatting, mypy type checking
- API safety verification (blocks real keys)
- Docker image building with Trivy scanning
- Pre-commit hook validation

**Critical Notes:**
- Use `mypy src/` not `mypy .` (avoids module conflicts)
- Use `docker compose` not `docker-compose`
- All tests automatically mocked

## Configuration

### config.json
```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 4000,
  "system_prompt": "Expert coding assistant with secure sandbox access for file operations"
}
```

### CLI Options
- `--config`: Configuration file path (default: `config.json`)
- `--model`: Override model from config

## Security Features

### API Safety
- Global test fixtures block real API calls
- CI validates against real API keys
- Mock responses for all Anthropic interactions
- Safe dummy keys in test environments

### Docker Security
- Non-root user (`appuser`)
- Resource limits (512M memory, 0.5 CPU)
- Network isolation
- Read-only mounts for config/source
- No privilege escalation
- Minimal Python slim base image
