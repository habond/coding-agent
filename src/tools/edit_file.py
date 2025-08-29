"""Edit file tool."""

import os
from typing import Any

from models import ToolMetadata


def edit_file(params: dict[str, Any]) -> str:
    """Edit a file by replacing text strings.

    Args:
        params: Dictionary containing:
            - file_path (str): Path to the file to edit
            - old_string (str): Text to search for and replace
            - new_string (str): Text to replace with
            - replace_all (bool, optional): Replace all occurrences. Default: False

    Returns:
        Success message with replacement count, or error message if operation fails
    """
    if not params or "file_path" not in params:
        return "Error: file_path parameter is required"

    if "old_string" not in params:
        return "Error: old_string parameter is required"

    if "new_string" not in params:
        return "Error: new_string parameter is required"

    file_path = params["file_path"]
    old_string = params["old_string"]
    new_string = params["new_string"]
    replace_all = params.get("replace_all", False)

    if not isinstance(file_path, str):
        return "Error: file_path must be a string"

    if not isinstance(old_string, str):
        return "Error: old_string must be a string"

    if not isinstance(new_string, str):
        return "Error: new_string must be a string"

    if not isinstance(replace_all, bool):
        return "Error: replace_all must be a boolean"

    # Security: Only allow editing files within the sandbox directory
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
            return f"Error: Access denied. Can only edit files within {sandbox_dir}"
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

        # Count occurrences
        count = content.count(old_string)

        if count == 0:
            return f"Error: String '{old_string}' not found in {file_path}"

        # Perform replacement
        if replace_all:
            new_content = content.replace(old_string, new_string)
            replacements_made = count
        else:
            # Replace only the first occurrence
            new_content = content.replace(old_string, new_string, 1)
            replacements_made = 1

        # Write the file back
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Success: Replaced {replacements_made} occurrence(s) in {file_path}"

    except PermissionError:
        return f"Error: Permission denied editing file - {file_path}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file as UTF-8 - {file_path}"
    except Exception as e:
        return f"Error: Failed to edit file - {str(e)}"


# Tool metadata for registration
TOOL_METADATA: ToolMetadata = {
    "name": "edit_file",
    "description": "Edit a file by replacing text strings in the sandbox directory",
    "handler": edit_file,
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to edit (must be within /app/sandbox)",
            },
            "old_string": {
                "type": "string",
                "description": "Text to search for and replace",
            },
            "new_string": {
                "type": "string",
                "description": "Text to replace with",
            },
            "replace_all": {
                "type": "boolean",
                "description": "Replace all occurrences (default: False - replace only first)",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    },
}
