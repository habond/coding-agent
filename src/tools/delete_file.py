"""Delete file tool."""

import os
from typing import Any


def delete_file(params: dict[str, Any]) -> str:
    """Delete a file within the sandbox directory.

    Args:
        params: Dictionary containing:
            - file_path (str): Path to the file to delete

    Returns:
        Success message or error message if file cannot be deleted
    """
    if not params or "file_path" not in params:
        return "Error: file_path parameter is required"

    file_path = params["file_path"]

    if not isinstance(file_path, str):
        return "Error: file_path must be a string"

    # Security: Only allow deleting files within the sandbox directory
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
            return f"Error: file_path must be within sandbox directory - {file_path}"

    except (OSError, ValueError) as e:
        return f"Error: Invalid file path - {str(e)}"

    try:
        # Check if file exists
        if not os.path.exists(abs_file_path):
            return f"Error: File not found - {file_path}"

        # Check if it's actually a file (not a directory)
        if not os.path.isfile(abs_file_path):
            return f"Error: Path is not a file - {file_path}"

        # Delete the file
        os.remove(abs_file_path)

        # Get relative path for user-friendly message
        rel_file_path = os.path.relpath(abs_file_path, abs_sandbox_dir)

        return f"Success: Deleted file '{rel_file_path}'"

    except PermissionError:
        return f"Error: Permission denied deleting file - {file_path}"
    except OSError as e:
        return f"Error: Failed to delete file - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during deletion - {str(e)}"


# Tool metadata for registration
TOOL_METADATA = {
    "name": "delete_file",
    "description": "Delete a file within the sandbox directory",
    "handler": delete_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to delete (within sandbox)",
            },
        },
        "required": ["file_path"],
    },
}
