# Claude CLI

[![CI](https://github.com/habond/coding-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/habond/coding-agent/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python command-line interface for interacting with Anthropic's Claude AI. Features real-time streaming responses, interactive REPL mode, and an extensible tool system with secure sandboxed file operations.

## Features

- 🔄 **Interactive REPL mode** - Ongoing conversations with context
- ⚡ **Real-time streaming** - See responses as they're generated
- 🛠️ **Extensible tool system** - Auto-discovered custom tools
- 📁 **Secure sandbox** - Isolated file operations (Docker)
- 🔒 **Type-safe** - Full mypy type checking
- 🧪 **API-safe testing** - Automatic mocking prevents charges

## Quick Start

### Prerequisites
- Python 3.11+ or Docker (recommended)
- Anthropic API key

### Installation

```bash
# Clone repository
git clone https://github.com/habond/coding-agent.git
cd coding-agent

# Set up API key
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### Usage

#### Docker (Recommended - Secure)
```bash
# Interactive mode
./run.sh

# Single message
./run.sh "What is the current time?"

# Direct docker-compose
docker compose run --rm claude-cli
```

#### Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
./run.sh --local
./run.sh --local "Your message"

# Or directly
python src/main.py
```

## Interactive Session Example

```
$ ./run.sh

========================================
[USER MESSAGE]
========================================

You: Create a Python fibonacci calculator and save it

========================================
[ASSISTANT MESSAGE]
========================================

Claude: I'll create a Python script that calculates Fibonacci numbers.

========================================
[TOOL CALL]
========================================

[Tool: write_file -> Success: File written to fibonacci.py (523 bytes)]

========================================
[ASSISTANT MESSAGE]
========================================

I've created a Fibonacci calculator at `/app/sandbox/fibonacci.py` with:
- Iterative calculation function
- Interactive input prompt
- Error handling for invalid inputs

You can run it to generate Fibonacci sequences. Would you like to see the contents or create tests?
```

## Built-in Tools

### File Operations
- `read_file` - Read files from sandbox
- `write_file` - Write/append files (auto-creates directories)
- `edit_file` - Find and replace text
- `list_files` - List directory contents
- `rename_file` - Rename or move files
- `move_file` - Move files between directories
- `delete_file` - Delete files

### Directory Operations
- `create_directory` - Create directories with parents
- `rename_directory` - Rename or move directories
- `delete_directory` - Delete directories (force option available)

All operations are restricted to the `/app/sandbox` directory for security.

## Creating Custom Tools

Add a new file to `src/tools/`:

```python
from typing import Any
from models import ToolMetadata

def my_tool(params: dict[str, Any]) -> str:
    """Tool implementation."""
    if "required_param" not in params:
        return "Error: required_param is required"

    # Tool logic
    return f"Success: Processed {params['required_param']}"

TOOL_METADATA: ToolMetadata = {
    "name": "my_tool",
    "description": "What this tool does",
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

Tools are automatically discovered and loaded.

## Development

### Testing
```bash
# Run all tests (automatically mocked - no API charges)
pytest

# Run specific test
pytest tests/test_chat.py::TestClaudeChat::test_send_message_no_tools -v

# With coverage
pytest --cov=src
```

### Code Quality
```bash
# Run all checks
pre-commit run --all-files

# Individual checks
ruff check --fix   # Lint and fix
ruff format       # Format code
mypy src/         # Type check
```

### Project Structure
```
├── src/
│   ├── main.py           # CLI entry point
│   ├── chat.py           # Claude API integration
│   ├── models.py         # Type definitions
│   └── tools/
│       ├── registry.py   # Tool management
│       └── *.py          # Individual tools
├── tests/                # Test suite with mocking
├── sandbox/              # Secure workspace
├── config.json          # Configuration
├── docker-compose.yml   # Docker setup
└── CLAUDE.md           # Claude Code instructions
```

## Configuration

Edit `config.json`:
```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 4000,
  "system_prompt": "Expert coding assistant with secure sandbox access"
}
```

CLI options:
- `--config` - Custom config file path
- `--model` - Override model selection

## Architecture

### Core Components
- **ClaudeChat** - Manages API communication and streaming
- **ToolRegistry** - Dynamic tool discovery and execution
- **Type System** - Strongly typed interfaces in `models.py`

### Streaming System
Uses Anthropic's streaming API for real-time output:
- Text appears as generated, not after completion
- Seamless tool integration maintains stream flow
- Clear visual boundaries between interactions

### Security
- **Sandbox isolation** - All file operations restricted to `/app/sandbox`
- **Docker security** - Non-root user, resource limits, read-only mounts
- **API safety** - Tests automatically mocked, no accidental charges
- **Path validation** - Prevents directory traversal attacks

## CI/CD

GitHub Actions provides:
- Multi-Python testing (3.11, 3.12)
- Code quality checks (ruff, mypy)
- API safety verification
- Docker security scanning with Trivy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests (automatically API-safe)
4. Ensure all checks pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
