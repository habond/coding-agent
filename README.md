# Claude CLI

[![CI](https://github.com/habond/coding-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/habond/coding-agent/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python command-line interface for interacting with Anthropic's Claude AI. Features both interactive REPL mode and single-message execution with an extensible tool system.

## Features

- 🔄 **Interactive REPL mode** for ongoing conversations
- ⚡ **Single-message mode** for quick queries
- 🌊 **Real-time streaming output** for immediate response feedback
- 🛠️ **Extensible tool system** with automatic discovery
- 📁 **Secure sandbox** for file operations (Docker isolated)
- 🐳 **Docker support** for secure, containerized execution
- ⚙️ **Configurable settings** via JSON and environment variables
- 🧪 **Comprehensive test suite** with API safety measures
- 🚀 **CI/CD ready** with GitHub Actions automation
- 🔒 **Cost-safe testing** with automatic API mocking
- 🏷️ **Type-safe code** with mypy static type checking
- 📊 **Clear conversation boundaries** with visual delimiters

## Quick Start

### Prerequisites

- Python 3.11+ OR Docker (recommended for security)
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/habond/coding-agent.git
   cd coding-agent
   ```

2. Set up your API key:
   ```bash
   echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
   ```

#### Option A: Docker (Recommended for Security)

No additional setup required! Docker containers are built automatically.

#### Option B: Local Python Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Docker Mode (Recommended - Secure Sandboxed Environment)

```bash
# Interactive REPL mode with streaming output
./run.sh

# Single message mode with streaming output
./run.sh "What is the current time?"

# With docker-compose directly
docker-compose run --rm claude-cli
docker-compose run --rm claude-cli python src/main.py "Your message"
```

**Interactive Mode Features:**
- Real-time streaming responses as Claude generates them
- Visual separators between user inputs, Claude responses, and tool calls
- Clear delineation with `========` borders for all interaction types
- Labeled interactions: [USER MESSAGE], [ASSISTANT MESSAGE], and [TOOL CALL]
- Consistent formatting with proper spacing and visual hierarchy
- Graceful handling of piped input and EOF conditions

#### Local Mode (Development)

```bash
# Interactive REPL mode
./run.sh --local

# Single message mode
./run.sh --local "What is the current time?"

# Direct Python execution
python src/main.py
python src/main.py "Your message"
```

#### Command Line Options
```bash
python src/main.py --help
```

Options:
- `--config`: Path to configuration file (default: `config.json`)
- `--model`: Override the model from config

## Configuration

The application can be configured via `config.json`:

```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 4000,
  "system_prompt": "Expert coding assistant with secure sandbox access for file operations"
}
```

The system prompt is optimized for coding assistance with emphasis on:
- Using the sandbox environment for file operations
- Providing practical programming solutions
- Code analysis and debugging capabilities

## Tools

The tool system allows extending Claude's capabilities. Tools are automatically loaded from the `src/tools/` directory.

### Built-in Tools

- **read_file**: Reads files within the secure sandbox directory
- **write_file**: Writes/appends to files within the sandbox (with auto-directory creation)
- **list_files**: Recursively lists files in sandbox directories
- **rename_file**: Renames or moves files within the sandbox directory

### Creating Custom Tools

Create a new Python file in `src/tools/` with the following structure:

```python
from typing import Any

def my_tool(params: dict[str, Any]) -> str:
    """Your tool implementation."""
    return "Tool result"

TOOL_METADATA = {
    "name": "my_tool",
    "description": "Description of what the tool does",
    "handler": my_tool,
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
}
```

## Development

### Running Tests

**Safe Testing**: All tests use automatic API mocking to prevent accidental charges.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chat.py

# Run tests by marker
pytest -m unit
```

**Note**: Tests automatically block real API calls and use mock responses. No risk of API charges during testing.

### Code Quality
```bash
# Lint code
ruff check

# Format code
ruff format

# Type check code
mypy src/

# Run pre-commit hooks (includes ruff, mypy, and tests)
pre-commit run --all-files
```

### Project Structure
```
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI/CD
├── src/
│   ├── main.py          # CLI entry point
│   ├── chat.py          # Claude API integration
│   └── tools/
│       ├── registry.py  # Tool management
│       └── *.py         # Individual tools
├── tests/
│   ├── conftest.py      # Test configuration & API safety
│   └── **/*.py          # Test suite with automatic mocking
├── sandbox/             # Secure working directory for file operations
│   └── .gitkeep        # Keeps directory in git
├── config.json         # Application configuration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker orchestration
├── pytest.ini         # Test configuration
├── mypy.ini           # Type checking configuration
├── .pre-commit-config.yaml  # Code quality hooks
├── run.sh             # Convenience script (Docker/local modes)
└── CLAUDE.md          # Claude Code assistant instructions
```

## Architecture

### Core Components

- **ClaudeCLI**: Main application class handling CLI arguments and modes
- **ClaudeChat**: Manages API communication, conversation state, and streaming responses
- **ToolRegistry**: Dynamically loads and executes tools

### Streaming Architecture

The application uses Anthropic's streaming API to provide real-time response output:
- **Immediate feedback**: Text appears as it's generated, not after completion
- **Tool integration**: Seamless streaming continues even when tools are invoked
- **Visual clarity**: Clear boundaries between different types of interactions

### Sandbox Environment

The `sandbox/` directory provides a secure workspace for file operations:
- Isolated from system files (security boundary enforced)
- Persistent between sessions
- Auto-creates nested directories as needed
- Docker container mounts this as `/app/sandbox`
- All file tools are restricted to this directory

### Tool System

Tools are discovered automatically using Python's `importlib`. Each tool defines metadata that describes its interface, allowing the system to:

- Generate API-compatible tool definitions
- Validate input parameters
- Execute tools safely with error handling

### Security & Safety

#### API Safety
The project includes comprehensive measures to prevent accidental API charges:
- **Automatic API mocking** in all tests via `tests/conftest.py`
- **CI/CD safety checks** that block real API keys
- **Test environment isolation** with safe dummy keys
- **Pre-commit hooks** that validate code quality without API calls

#### Docker Security
The Docker setup provides multiple security layers:
- **Non-root user**: Application runs as unprivileged user `appuser`
- **Resource limits**: Memory (512M) and CPU (0.5) constraints
- **Network isolation**: Dedicated Docker network
- **Read-only mounts**: Configuration files mounted as read-only
- **Sandbox isolation**: File operations restricted to `/app/sandbox`
- **No privilege escalation**: Security options prevent elevation

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Multi-Python testing** (3.11, 3.12)
- **Code quality checks** (ruff linting, formatting, mypy type checking)
- **Automated testing** with API safety guarantees
- **Pre-commit validation** ensuring code standards

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality (automatically API-safe)
5. Run the test suite and linting
6. Submit a pull request

All tests are automatically safe - no risk of API charges during development.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
