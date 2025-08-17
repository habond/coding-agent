# Claude CLI

A Python command-line interface for interacting with Anthropic's Claude AI. Features both interactive REPL mode and single-message execution with an extensible tool system.

## Features

- 🔄 **Interactive REPL mode** for ongoing conversations
- ⚡ **Single-message mode** for quick queries
- 🛠️ **Extensible tool system** with automatic discovery
- 📝 **Debug logging** with conversation history
- ⚙️ **Configurable settings** via JSON and environment variables
- 🧪 **Comprehensive test suite** with mocking

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
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

#### Command Line Options
```bash
python src/main.py --help
```

Options:
- `--config`: Path to configuration file (default: `config.json`)
- `--model`: Override the model from config
- `--debug`: Enable debug mode
- `--no-debug`: Disable debug mode

## Configuration

The application can be configured via `config.json`:

```json
{
  "model": "claude-3-haiku-20240307",
  "max_tokens": 1000,
  "system_prompt": "You are a helpful AI assistant. Be concise and clear in your responses.",
  "debug": true,
  "debug_file": "logs/debug.json",
  "features": {
    "tools_enabled": true,
    "save_conversations": false
  }
}
```

## Tools

The tool system allows extending Claude's capabilities. Tools are automatically loaded from the `src/tools/` directory.

### Built-in Tools

- **get_current_time**: Returns the current date and time
- **sort_data**: Sorts data in various formats (JSON arrays, CSV, etc.)

### Creating Custom Tools

Create a new Python file in `src/tools/` with the following structure:

```python
def my_tool(params: dict) -> str:
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

### Code Quality
```bash
# Lint code
ruff check

# Format code
ruff format

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure
```
├── src/
│   ├── main.py          # CLI entry point
│   ├── chat.py          # Claude API integration
│   └── tools/
│       ├── registry.py  # Tool management
│       └── *.py         # Individual tools
├── tests/               # Test suite
├── config.json         # Application configuration
├── requirements.txt    # Python dependencies
├── pytest.ini         # Test configuration
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

### Debug Logging

When debug mode is enabled, all conversation history is logged to `logs/debug.json` for troubleshooting and development.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
