"""Write file tool."""

import os
from typing import Any


def write_file(params: dict[str, Any]) -> str:
    """Write content to a file in the sandbox directory.

    Args:
        params: Dictionary containing:
            - file_path (str): Path to the file to write
            - content (str): Content to write to the file
            - mode (str, optional): Write mode - 'w' (overwrite) or 'a' (append). Default: 'w'

    Returns:
        Success message or error message if file cannot be written
    """
    if not params or "file_path" not in params:
        return "Error: file_path parameter is required"

    if "content" not in params:
        return "Error: content parameter is required"

    file_path = params["file_path"]
    content = params["content"]
    mode = params.get("mode", "w")

    if not isinstance(file_path, str):
        return "Error: file_path must be a string"

    if not isinstance(content, str):
        return "Error: content must be a string"

    if mode not in ["w", "a"]:
        return "Error: mode must be 'w' (write/overwrite) or 'a' (append)"

    # Security: Only allow writing files within the sandbox directory
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
            return f"Error: Access denied. Can only write files within {sandbox_dir}"
    except Exception as e:
        return f"Error: Invalid file path - {str(e)}"

    try:
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(abs_file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # Write the file
        with open(abs_file_path, mode, encoding="utf-8") as f:
            f.write(content)

        action = "appended to" if mode == "a" else "written to"
        file_size = len(content.encode("utf-8"))
        return f"Success: Content {action} {file_path} ({file_size} bytes)"

    except PermissionError:
        return f"Error: Permission denied writing to file - {file_path}"
    except OSError as e:
        return f"Error: Failed to create directory or write file - {str(e)}"
    except Exception as e:
        return f"Error: Failed to write file - {str(e)}"


# Tool metadata for registration
TOOL_METADATA = {
    "name": "write_file",
    "description": "Write content to a file in the sandbox directory",
    "handler": write_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write (must be within /app/sandbox)",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
            "mode": {
                "type": "string",
                "description": "Write mode: 'w' to overwrite (default) or 'a' to append",
                "enum": ["w", "a"],
            },
        },
        "required": ["file_path", "content"],
    },
}
