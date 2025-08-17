# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Python CLI application for interacting with Claude AI through the Anthropic API. The application supports both interactive REPL mode and single-message execution, with an extensible tool system for adding custom capabilities.

## Development Commands

### Running the Application

#### Default (Docker - Recommended for Security)
```bash
# Interactive REPL mode (Docker)
./run.sh

# Single message mode (Docker)
./run.sh "Your message here"

# Show help
./run.sh --help
```

#### Local Development (Optional)
```bash
# Interactive REPL mode (local venv)
./run.sh --local

# Single message mode (local venv)
./run.sh --local "Your message here"

# Using Python directly (requires venv setup)
python src/main.py
```

#### Manual Docker Usage
```bash
# Build and run with docker-compose (recommended)
docker-compose up claude-cli

# Interactive mode
docker-compose run --rm claude-cli

# Single message mode
docker-compose run --rm claude-cli python src/main.py "Your message here"

# Development mode with shell access
docker-compose run --rm claude-cli-dev

# Build manually
docker build -t claude-cli .
docker run -it --rm -v ./.env:/app/.env:ro claude-cli
```

**Security Note**: Docker containerization provides isolation and sandboxing for tool execution, preventing potential security risks from affecting the host system.

### Testing

#### Local Testing
```bash
# Run all tests (API-safe, no charges)
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chat.py

# Run tests with specific marker
pytest -m unit
```

#### Docker Testing
```bash
# Run tests in container
docker-compose run --rm claude-cli pytest

# Run tests with verbose output
docker-compose run --rm claude-cli pytest -v

# Run specific test file in container
docker-compose run --rm claude-cli pytest tests/test_chat.py
```

**Important**: All tests automatically use API mocking via `tests/conftest.py`. No real API calls are made during testing.

### Code Quality

#### Local Code Quality
```bash
# Check code style and lint
ruff check

# Format code
ruff format

# Type check code
mypy src/

# Run pre-commit hooks (includes ruff, mypy, and pytest)
pre-commit run --all-files
```

#### Docker Code Quality
```bash
# Check code style and lint in container
docker-compose run --rm claude-cli ruff check

# Format code in container
docker-compose run --rm claude-cli ruff format

# Type check code in container
docker-compose run --rm claude-cli mypy src/
```

## Architecture

### Core Components

- **`src/main.py`**: Entry point with CLI argument parsing and application setup
- **`src/chat.py`**: `ClaudeChat` class that manages API communication, conversation state, and tool execution
- **`src/tools/registry.py`**: `ToolRegistry` class for dynamic tool loading and management
- **`src/tools/`**: Individual tool implementations with `TOOL_METADATA` for auto-registration

### Tool System
Tools are automatically loaded from the `src/tools/` directory. Each tool file must define:
- A handler function that takes `params: dict[str, Any]` and returns a string (with proper type annotations)
- `TOOL_METADATA` dictionary with `name`, `description`, `handler`, and `input_schema`

#### Available Tools
- **`read_file`**: Reads the full contents of files within the sandbox directory
- **`write_file`**: Writes content to files within the sandbox directory (supports overwrite and append modes)
- **`list_files`**: Recursively lists all files in a directory within the sandbox

#### Sandbox Directory
The `sandbox/` directory serves as a secure working area for the AI assistant:
- Mounted as `/app/sandbox` in the Docker container
- Provides isolated file system access for tool operations
- Persistent between container runs
- Safe for file creation, modification, and execution
- Security-restricted to prevent access outside the sandbox
- Supports automatic directory creation for nested paths
- File operations include read, write (overwrite), and append modes

#### Tool Usage Examples
```bash
# Read a file
./run.sh "Read the file /app/sandbox/example.txt"

# Write a new file (overwrites if exists)
./run.sh "Write 'Hello World' to /app/sandbox/greeting.txt"

# Append to a file
./run.sh "Append '\nNew line' to /app/sandbox/greeting.txt using append mode"

# Create a file in a subdirectory (auto-creates directories)
./run.sh "Create a Python script at /app/sandbox/scripts/test.py"
```


### Configuration
The application uses `config.json` for settings including model selection and feature flags. Environment variables are loaded from `.env` file.

#### Default Configuration
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
- Proper use of sandbox file paths (/app/sandbox/)

### Type Checking
The project uses mypy for static type checking with configuration in `mypy.ini`:
- Comprehensive type annotations throughout the codebase
- Strict type checking for better code quality and developer experience
- Type-safe handling of Anthropic API responses
- Integrated into pre-commit hooks and CI/CD pipeline

### Key Dependencies
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `pytest`: Testing framework
- `ruff`: Code linting and formatting
- `mypy`: Static type checking
- `pre-commit`: Git hooks for code quality

### Testing Structure
Tests use pytest with comprehensive API safety measures:
- `tests/conftest.py` automatically mocks all Anthropic API calls
- Python path setup for importing from `src/`
- Test files follow the pattern `test_*.py` in the `tests/` directory
- Automatic blocking of real API calls with error messages
- Safe API key injection for test environments

### CI/CD Pipeline
GitHub Actions workflow (`.github/workflows/ci.yml`) provides:
- Multi-Python version testing (3.11, 3.12)
- Code quality validation (ruff linting/formatting, mypy type checking)
- API safety verification (blocks real API keys)
- Pre-commit hook validation including pytest

### API Safety Measures
The codebase includes multiple layers of protection against accidental API charges:
- Global test fixtures that block real API calls
- CI environment validation that rejects real API keys
- Mock responses for all Anthropic client interactions
- Safe dummy API keys in test environments

### Docker Security Features
The Docker setup provides additional security layers:
- **Non-root user**: Application runs as unprivileged user `appuser`
- **Resource limits**: Memory (512M) and CPU (0.5) constraints prevent resource exhaustion
- **Network isolation**: Dedicated Docker network with controlled access
- **Read-only mounts**: Configuration and source files mounted as read-only
- **No new privileges**: Security option prevents privilege escalation
- **Minimal base image**: Python slim image reduces attack surface
- **Environment isolation**: API keys and sensitive data isolated within container
