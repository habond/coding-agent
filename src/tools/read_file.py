"""Read file tool."""

import os
from typing import Any

from models import ToolMetadata


def read_file(params: dict[str, Any]) -> str:
    """Read the full contents of a file.

    Args:
        params: Dictionary containing:
            - file_path (str): Path to the file to read

    Returns:
        File contents as a string, or error message if file cannot be read
    """
    if not params or "file_path" not in params:
        return "Error: file_path parameter is required"

    file_path = params["file_path"]

    if not isinstance(file_path, str):
        return "Error: file_path must be a string"

    # Security: Only allow reading files within the sandbox directory
    sandbox_dir = "/app/sandbox"

    # Convert to absolute path and normalize
    try:
        abs_file_path = os.path.abspath(file_path)
        abs_sandbox_dir = os.path.abspath(sandbox_dir)

        # Check if the file is within the sandbox directory
        if (
            not abs_file_path.startswith(abs_sandbox_dir + os.sep)
            and abs_file_path != abs_sandbox_dir
        ):
            return f"Error: Access denied. Can only read files within {sandbox_dir}"
    except Exception as e:
        return f"Error: Invalid file path - {str(e)}"

    try:
        # Check if file exists
        if not os.path.exists(abs_file_path):
            return f"Error: File not found - {file_path}"

        # Check if it's actually a file (not a directory)
        if not os.path.isfile(abs_file_path):
            return f"Error: Path is not a file - {file_path}"

        # Read the file
        with open(abs_file_path, encoding="utf-8") as f:
            content = f.read()

        return content

    except PermissionError:
        return f"Error: Permission denied reading file - {file_path}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file as UTF-8 - {file_path}"
    except Exception as e:
        return f"Error: Failed to read file - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "read_file",
    "description": "Read the full contents of a file from the sandbox directory",
    "handler": read_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read (must be within /app/sandbox)",
            }
        },
        "required": ["file_path"],
    },
}
