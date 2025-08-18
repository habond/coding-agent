"""Rename file tool."""

import os
from typing import Any


def rename_file(params: dict[str, Any]) -> str:
    """Rename a file within the sandbox directory.

    Args:
        params: Dictionary containing:
            - old_path (str): Current path to the file to rename
            - new_path (str): New path/name for the file

    Returns:
        Success message or error message if file cannot be renamed
    """
    if not params or "old_path" not in params:
        return "Error: old_path parameter is required"

    if "new_path" not in params:
        return "Error: new_path parameter is required"

    old_path = params["old_path"]
    new_path = params["new_path"]

    if not isinstance(old_path, str):
        return "Error: old_path must be a string"

    if not isinstance(new_path, str):
        return "Error: new_path must be a string"

    # Security: Only allow renaming files within the sandbox directory
    sandbox_dir = "/app/sandbox"

    # Convert to absolute paths and normalize
    try:
        abs_old_path = os.path.abspath(old_path)
        abs_new_path = os.path.abspath(new_path)
        abs_sandbox_dir = os.path.abspath(sandbox_dir)

        # Check if both paths are within the sandbox directory
        if (
            not abs_old_path.startswith(abs_sandbox_dir + os.sep)
            and abs_old_path != abs_sandbox_dir
        ):
            return f"Error: old_path must be within sandbox directory - {old_path}"

        if (
            not abs_new_path.startswith(abs_sandbox_dir + os.sep)
            and abs_new_path != abs_sandbox_dir
        ):
            return f"Error: new_path must be within sandbox directory - {new_path}"

    except (OSError, ValueError) as e:
        return f"Error: Invalid file path - {str(e)}"

    try:
        # Check if source file exists
        if not os.path.exists(abs_old_path):
            return f"Error: Source file not found - {old_path}"

        # Check if source is actually a file (not a directory)
        if not os.path.isfile(abs_old_path):
            return f"Error: Source path is not a file - {old_path}"

        # Check if destination already exists
        if os.path.exists(abs_new_path):
            return f"Error: Destination already exists - {new_path}"

        # Create destination directory if it doesn't exist
        new_dir = os.path.dirname(abs_new_path)
        if new_dir and not os.path.exists(new_dir):
            os.makedirs(new_dir, exist_ok=True)

        # Perform the rename/move operation
        os.rename(abs_old_path, abs_new_path)

        # Get relative paths for user-friendly message
        rel_old_path = os.path.relpath(abs_old_path, abs_sandbox_dir)
        rel_new_path = os.path.relpath(abs_new_path, abs_sandbox_dir)

        return f"Success: Renamed '{rel_old_path}' to '{rel_new_path}'"

    except PermissionError:
        return f"Error: Permission denied renaming file - {old_path}"
    except OSError as e:
        return f"Error: Failed to rename file - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during rename - {str(e)}"


# Tool metadata for registration
TOOL_METADATA = {
    "name": "rename_file",
    "description": "Rename or move a file within the sandbox directory",
    "handler": rename_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "old_path": {
                "type": "string",
                "description": "Current path to the file to rename (within sandbox)",
            },
            "new_path": {
                "type": "string",
                "description": "New path/name for the file (within sandbox)",
            },
        },
        "required": ["old_path", "new_path"],
    },
}
