"""Delete directory tool."""

import os
import shutil
from typing import Any

from models import ToolMetadata


def delete_directory(params: dict[str, Any]) -> str:
    """Delete a directory and all its contents within the sandbox directory.

    Args:
        params: Dictionary containing:
            - directory_path (str): Path to the directory to delete
            - force (bool, optional): Force deletion even if not empty. Default: False

    Returns:
        Success message or error message if directory cannot be deleted
    """
    if not params or "directory_path" not in params:
        return "Error: directory_path parameter is required"

    directory_path = params["directory_path"]
    force = params.get("force", False)

    if not isinstance(directory_path, str):
        return "Error: directory_path must be a string"

    if not isinstance(force, bool):
        return "Error: force must be a boolean"

    # Security: Only allow deleting directories within the sandbox directory
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
            return f"Error: Access denied. Can only delete directories within {sandbox_dir}"

        # Prevent deleting the sandbox root
        if abs_dir_path == abs_sandbox_dir:
            return "Error: Cannot delete the sandbox root directory"

    except Exception as e:
        return f"Error: Invalid directory path - {str(e)}"

    try:
        # Check if directory exists
        if not os.path.exists(abs_dir_path):
            return f"Error: Directory not found - {directory_path}"

        # Check if it's actually a directory
        if not os.path.isdir(abs_dir_path):
            return f"Error: Path is not a directory - {directory_path}"

        # Check if directory is empty (unless force is True)
        if not force and os.listdir(abs_dir_path):
            return (
                f"Error: Directory is not empty - {directory_path}. "
                "Use force=true to delete non-empty directories"
            )

        # Delete the directory
        if force:
            # Remove directory and all contents
            shutil.rmtree(abs_dir_path)
        else:
            # Remove empty directory only
            os.rmdir(abs_dir_path)

        # Get relative path for user-friendly message
        rel_dir_path = os.path.relpath(abs_dir_path, abs_sandbox_dir)

        return f"Success: Deleted directory '{rel_dir_path}'"

    except PermissionError:
        return f"Error: Permission denied deleting directory - {directory_path}"
    except OSError as e:
        return f"Error: Failed to delete directory - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during deletion - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "delete_directory",
    "description": "Delete a directory within the sandbox directory",
    "handler": delete_directory,
    "input_schema": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to the directory to delete (must be within /app/sandbox)",
            },
            "force": {
                "type": "boolean",
                "description": "Force deletion even if directory is not empty (default: False)",
            },
        },
        "required": ["directory_path"],
    },
}
