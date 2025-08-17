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
- 🛠️ **Extensible tool system** with automatic discovery
- ⚙️ **Configurable settings** via JSON and environment variables
- 🧪 **Comprehensive test suite** with API safety measures
- 🚀 **CI/CD ready** with GitHub Actions automation
- 🔒 **Cost-safe testing** with automatic API mocking
- 🏷️ **Type-safe code** with mypy static type checking

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/habond/coding-agent.git
   cd coding-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API key:
   ```bash
   echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
   ```

### Usage

#### Interactive Mode
```bash
./run.sh
```

#### Single Message Mode
```bash
./run.sh "What is the current time?"
```

#### Tool-Free Mode
For questions that can be answered using Claude's internal knowledge without tools:
```bash
./run.sh --no-tools "What is the distance from Earth to the Moon?"
./run.sh --no-tools "What is 2+2?"
```

#### Command Line Options
```bash
python src/main.py --help
```

Options:
- `--config`: Path to configuration file (default: `config.json`)
- `--model`: Override the model from config
- `--no-tools`: Disable tools and use Claude's internal knowledge only

## Configuration

The application can be configured via `config.json`:

```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 1000,
  "system_prompt": "You are a helpful AI assistant. Be concise and clear in your responses."
}
```

## Tools

The tool system allows extending Claude's capabilities. Tools are automatically loaded from the `src/tools/` directory.

When tools are available, Claude may prefer to use them even for questions it can answer with internal knowledge. Use the `--no-tools` flag to bypass this behavior and get direct answers from Claude's training data.

### Built-in Tools

- **get_current_time**: Returns the current date and time
- **sort_data**: Sorts data in various formats (JSON arrays, CSV, etc.)

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
├── config.json         # Application configuration
├── requirements.txt    # Python dependencies
├── pytest.ini         # Test configuration
├── mypy.ini           # Type checking configuration
├── .pre-commit-config.yaml  # Code quality hooks
└── run.sh             # Convenience script
```

## Architecture

### Core Components

- **ClaudeCLI**: Main application class handling CLI arguments and modes
- **ClaudeChat**: Manages API communication and conversation state
- **ToolRegistry**: Dynamically loads and executes tools

### Tool System

Tools are discovered automatically using Python's `importlib`. Each tool defines metadata that describes its interface, allowing the system to:

- Generate API-compatible tool definitions
- Validate input parameters
- Execute tools safely with error handling

### API Safety

The project includes comprehensive safety measures to prevent accidental API charges:

- **Automatic API mocking** in all tests via `tests/conftest.py`
- **CI/CD safety checks** that block real API keys
- **Test environment isolation** with safe dummy keys
- **Pre-commit hooks** that validate code quality without API calls

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
