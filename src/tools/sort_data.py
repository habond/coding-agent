"""Sort data tool."""

import json
from typing import Any


def sort_data(params: dict[str, Any]) -> str:
    """Sort data in various formats.

    Args:
        params: Dictionary containing:
            - data: The data to sort (string, list, or JSON string)
            - order: "asc" (ascending) or "desc" (descending), default "asc"
            - numeric: True to sort as numbers, False for text, default False
            - case_sensitive: True for case-sensitive sorting, default False

    Returns:
        Sorted data as a string
    """
    try:
        data = params.get("data", "")
        order = params.get("order", "asc").lower()
        numeric = params.get("numeric", False)
        case_sensitive = params.get("case_sensitive", False)

        if not data:
            return "Error: No data provided to sort"

        # Try to parse as JSON first
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                data_list = parsed_data
            else:
                return "Error: JSON data must be a list/array"
        except json.JSONDecodeError:
            # If not JSON, treat as comma-separated values or newline-separated
            if "," in data:
                data_list = [item.strip() for item in data.split(",")]
            else:
                data_list = [item.strip() for item in data.split("\n") if item.strip()]

        if not data_list:
            return "Error: No data to sort"

        # Convert to appropriate type for sorting
        if numeric:
            try:
                # Try to convert to numbers
                converted_data = []
                for item in data_list:
                    if isinstance(item, int | float):
                        converted_data.append(item)
                    else:
                        # Try to parse as number
                        str_item = str(item).strip()
                        if "." in str_item:
                            converted_data.append(float(str_item))
                        else:
                            converted_data.append(int(str_item))
                data_list = converted_data
            except ValueError:
                return "Error: Could not convert data to numbers for numeric sorting"
        else:
            # Convert to strings for text sorting
            data_list = [str(item) for item in data_list]
            if not case_sensitive:
                # Sort by lowercase but preserve original case in output
                data_list.sort(key=str.lower, reverse=(order == "desc"))
            else:
                data_list.sort(reverse=(order == "desc"))

        # Sort the data
        if numeric or case_sensitive:
            data_list.sort(reverse=(order == "desc"))

        # Format output
        if all(isinstance(item, int | float) for item in data_list):
            # Return as JSON array for numbers
            return json.dumps(data_list)
        else:
            # Return as comma-separated for strings
            return ", ".join(str(item) for item in data_list)

    except Exception as e:
        return f"Error sorting data: {str(e)}"


# Tool metadata for registration
TOOL_METADATA = {
    "name": "sort_data",
    "description": "Sort data in ascending or descending order. Supports numbers, text, JSON arrays, and comma/newline separated values.",
    "handler": sort_data,
    "input_schema": {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "Data to sort - can be JSON array, comma-separated values, or newline-separated values",
            },
            "order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "Sort order: 'asc' for ascending, 'desc' for descending",
                "default": "asc",
            },
            "numeric": {
                "type": "boolean",
                "description": "Whether to sort as numbers (true) or text (false)",
                "default": False,
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether sorting should be case-sensitive",
                "default": False,
            },
        },
        "required": ["data"],
    },
}
