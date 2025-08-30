"""Create directory tool."""

import os
from typing import Any

from models import ToolMetadata


def create_directory(params: dict[str, Any]) -> str:
    """Create a directory within the sandbox directory.

    Args:
        params: Dictionary containing:
            - directory_path (str): Path to the directory to create

    Returns:
        Success message or error message if directory cannot be created
    """
    if not params or "directory_path" not in params:
        return "Error: directory_path parameter is required"

    directory_path = params["directory_path"]

    if not isinstance(directory_path, str):
        return "Error: directory_path must be a string"

    # Security: Only allow creating directories within the sandbox directory
    sandbox_dir = "/app/sandbox"

    # Convert to absolute path and normalize
    try:
        abs_dir_path = os.path.abspath(directory_path)
        abs_sandbox_dir = os.path.abspath(sandbox_dir)

        # Check if the directory is within the sandbox directory
        if (
            not abs_dir_path.startswith(abs_sandbox_dir + os.sep)
            and abs_dir_path != abs_sandbox_dir
        ):
            return f"Error: Access denied. Can only create directories within {sandbox_dir}"
    except Exception as e:
        return f"Error: Invalid directory path - {str(e)}"

    try:
        # Check if directory already exists
        if os.path.exists(abs_dir_path):
            if os.path.isdir(abs_dir_path):
                return f"Error: Directory already exists - {directory_path}"
            else:
                return f"Error: Path exists but is not a directory - {directory_path}"

        # Create the directory (including parent directories if needed)
        os.makedirs(abs_dir_path)

        # Get relative path for user-friendly message
        rel_dir_path = os.path.relpath(abs_dir_path, abs_sandbox_dir)

        return f"Success: Created directory '{rel_dir_path}'"

    except PermissionError:
        return f"Error: Permission denied creating directory - {directory_path}"
    except OSError as e:
        return f"Error: Failed to create directory - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during creation - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "create_directory",
    "description": "Create a directory within the sandbox directory",
    "handler": create_directory,
    "input_schema": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to the directory to create (must be within /app/sandbox)",
            }
        },
        "required": ["directory_path"],
    },
}
