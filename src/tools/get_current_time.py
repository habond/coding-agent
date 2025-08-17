"""Get current time tool."""

from datetime import datetime
from typing import Any


def get_current_time(params: dict[str, Any] = None) -> str:
    """Get the current date and time.

    Args:
        params: Parameters (not used for this tool)

    Returns:
        Current date and time as a formatted string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


# Tool metadata for registration
TOOL_METADATA = {
    "name": "get_current_time",
    "description": "Get the current date and time",
    "handler": get_current_time,
    "input_schema": {"type": "object", "properties": {}, "required": []},
}
