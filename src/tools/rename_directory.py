"""Rename directory tool."""

import os
import shutil
from typing import Any

from models import ToolMetadata


def rename_directory(params: dict[str, Any]) -> str:
    """Rename or move a directory within the sandbox directory.

    Args:
        params: Dictionary containing:
            - old_path (str): Current path of the directory
            - new_path (str): New path for the directory

    Returns:
        Success message or error message if directory cannot be renamed
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

    # Security: Only allow renaming directories within the sandbox directory
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
            return (
                f"Error: Access denied. Source directory must be within {sandbox_dir}"
            )

        if (
            not abs_new_path.startswith(abs_sandbox_dir + os.sep)
            and abs_new_path != abs_sandbox_dir
        ):
            return f"Error: Access denied. Destination must be within {sandbox_dir}"

        # Prevent renaming the sandbox root
        if abs_old_path == abs_sandbox_dir:
            return "Error: Cannot rename the sandbox root directory"

    except Exception as e:
        return f"Error: Invalid directory path - {str(e)}"

    try:
        # Check if source directory exists
        if not os.path.exists(abs_old_path):
            return f"Error: Directory not found - {old_path}"

        # Check if source is actually a directory
        if not os.path.isdir(abs_old_path):
            return f"Error: Path is not a directory - {old_path}"

        # Check if destination already exists
        if os.path.exists(abs_new_path):
            return f"Error: Destination already exists - {new_path}"

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(abs_new_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Rename/move the directory
        shutil.move(abs_old_path, abs_new_path)

        # Get relative paths for user-friendly message
        rel_old_path = os.path.relpath(abs_old_path, abs_sandbox_dir)
        rel_new_path = os.path.relpath(abs_new_path, abs_sandbox_dir)

        return f"Success: Renamed directory '{rel_old_path}' to '{rel_new_path}'"

    except PermissionError:
        return f"Error: Permission denied renaming directory - {old_path}"
    except OSError as e:
        return f"Error: Failed to rename directory - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during rename - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "rename_directory",
    "description": "Rename or move a directory within the sandbox directory",
    "handler": rename_directory,
    "input_schema": {
        "type": "object",
        "properties": {
            "old_path": {
                "type": "string",
                "description": "Current path of the directory (must be within /app/sandbox)",
            },
            "new_path": {
                "type": "string",
                "description": "New path for the directory (must be within /app/sandbox)",
            },
        },
        "required": ["old_path", "new_path"],
    },
}
