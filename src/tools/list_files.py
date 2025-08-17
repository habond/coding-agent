"""List files tool."""

import os
from typing import Any


def list_files(params: dict[str, Any]) -> str:
    """Recursively list all files in a directory.

    Args:
        params: Dictionary containing:
            - directory_path (str): Path to the directory to list (optional, defaults to /app/sandbox)
            - show_hidden (bool): Whether to show hidden files (optional, defaults to False)

    Returns:
        List of files as a string, or error message if directory cannot be read
    """
    # Default to sandbox directory if no path provided
    directory_path = params.get("directory_path", "/app/sandbox")
    show_hidden = params.get("show_hidden", False)

    if not isinstance(directory_path, str):
        return "Error: directory_path must be a string"

    if not isinstance(show_hidden, bool):
        return "Error: show_hidden must be a boolean"

    # Security: Only allow listing files within the sandbox directory
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
            return f"Error: Access denied. Can only list files within {sandbox_dir}"
    except Exception as e:
        return f"Error: Invalid directory path - {str(e)}"

    try:
        # Check if directory exists
        if not os.path.exists(abs_dir_path):
            return f"Error: Directory not found - {directory_path}"

        # Check if it's actually a directory
        if not os.path.isdir(abs_dir_path):
            return f"Error: Path is not a directory - {directory_path}"

        # Recursively collect all files
        all_files = []

        for root, dirs, files in os.walk(abs_dir_path):
            # Filter out hidden directories if show_hidden is False
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                # Filter out hidden files if show_hidden is False
                if not show_hidden and file.startswith("."):
                    continue

                file_path = os.path.join(root, file)
                # Always show full path starting from sandbox
                if file_path.startswith("/app/sandbox"):
                    display_path = file_path
                else:
                    # Convert back to sandbox-relative path for display
                    relative_path = os.path.relpath(file_path, abs_sandbox_dir)
                    display_path = os.path.join("/app/sandbox", relative_path)
                all_files.append(display_path)

        if not all_files:
            return f"No files found in {directory_path}"

        # Sort files for consistent output
        all_files.sort()

        # Format output
        file_count = len(all_files)
        result = f"Found {file_count} file{'s' if file_count != 1 else ''} in {directory_path}:\n\n"
        result += "\n".join(all_files)

        return result

    except PermissionError:
        return f"Error: Permission denied accessing directory - {directory_path}"
    except Exception as e:
        return f"Error: Failed to list files - {str(e)}"


# Tool metadata for registration
TOOL_METADATA = {
    "name": "list_files",
    "description": "Recursively list all files in a directory within the sandbox",
    "handler": list_files,
    "input_schema": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to the directory to list (must be within /app/sandbox, defaults to /app/sandbox if not specified)",
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Whether to show hidden files and directories (defaults to False)",
            },
        },
        "required": [],
    },
}
