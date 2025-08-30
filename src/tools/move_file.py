"""Move file tool."""

import os
import shutil
from typing import Any

from models import ToolMetadata


def move_file(params: dict[str, Any]) -> str:
    """Move a file from one directory to another within the sandbox.

    Args:
        params: Dictionary containing:
            - source_path (str): Current path of the file
            - destination_dir (str): Directory to move the file to
            - new_name (str, optional): New name for the file. If not provided, keeps original name

    Returns:
        Success message or error message if file cannot be moved
    """
    if not params or "source_path" not in params:
        return "Error: source_path parameter is required"

    if "destination_dir" not in params:
        return "Error: destination_dir parameter is required"

    source_path = params["source_path"]
    destination_dir = params["destination_dir"]
    new_name = params.get("new_name", None)

    if not isinstance(source_path, str):
        return "Error: source_path must be a string"

    if not isinstance(destination_dir, str):
        return "Error: destination_dir must be a string"

    if new_name is not None and not isinstance(new_name, str):
        return "Error: new_name must be a string"

    # Security: Only allow moving files within the sandbox directory
    sandbox_dir = "/app/sandbox"

    # Convert to absolute paths and normalize
    try:
        abs_source_path = os.path.abspath(source_path)
        abs_dest_dir = os.path.abspath(destination_dir)
        abs_sandbox_dir = os.path.abspath(sandbox_dir)

        # Check if both paths are within the sandbox directory
        if (
            not abs_source_path.startswith(abs_sandbox_dir + os.sep)
            and abs_source_path != abs_sandbox_dir
        ):
            return f"Error: Access denied. Source file must be within {sandbox_dir}"

        if (
            not abs_dest_dir.startswith(abs_sandbox_dir + os.sep)
            and abs_dest_dir != abs_sandbox_dir
        ):
            return f"Error: Access denied. Destination must be within {sandbox_dir}"

    except Exception as e:
        return f"Error: Invalid path - {str(e)}"

    try:
        # Check if source file exists
        if not os.path.exists(abs_source_path):
            return f"Error: File not found - {source_path}"

        # Check if source is actually a file
        if not os.path.isfile(abs_source_path):
            return f"Error: Path is not a file - {source_path}"

        # Determine the destination file path
        if new_name:
            # Use the provided new name
            dest_filename = new_name
        else:
            # Keep the original filename
            dest_filename = os.path.basename(abs_source_path)

        abs_dest_path = os.path.join(abs_dest_dir, dest_filename)

        # Check if destination file already exists
        if os.path.exists(abs_dest_path):
            return f"Error: Destination file already exists - {abs_dest_path}"

        # Create destination directory if it doesn't exist
        if not os.path.exists(abs_dest_dir):
            os.makedirs(abs_dest_dir, exist_ok=True)
        elif not os.path.isdir(abs_dest_dir):
            return f"Error: Destination path exists but is not a directory - {destination_dir}"

        # Move the file
        shutil.move(abs_source_path, abs_dest_path)

        # Get relative paths for user-friendly message
        rel_source_path = os.path.relpath(abs_source_path, abs_sandbox_dir)
        rel_dest_path = os.path.relpath(abs_dest_path, abs_sandbox_dir)

        return f"Success: Moved file '{rel_source_path}' to '{rel_dest_path}'"

    except PermissionError:
        return f"Error: Permission denied moving file - {source_path}"
    except OSError as e:
        return f"Error: Failed to move file - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during move - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "move_file",
    "description": "Move a file from one directory to another within the sandbox",
    "handler": move_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "Current path of the file (must be within /app/sandbox)",
            },
            "destination_dir": {
                "type": "string",
                "description": "Directory to move the file to (must be within /app/sandbox)",
            },
            "new_name": {
                "type": "string",
                "description": "Optional: New name for the file. If not provided, keeps original name",
            },
        },
        "required": ["source_path", "destination_dir"],
    },
}
