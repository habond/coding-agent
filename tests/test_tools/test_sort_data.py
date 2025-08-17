"""Tests for sort_data tool."""

import json

from tools.sort_data import TOOL_METADATA, sort_data


class TestSortData:
    """Test cases for sort_data tool."""

    def test_sort_numbers_ascending(self):
        """Test sorting numbers in ascending order."""
        params = {"data": "5,3,8,1", "numeric": True, "order": "asc"}
        result = sort_data(params)
        expected = [1, 3, 5, 8]
        assert json.loads(result) == expected

    def test_sort_numbers_descending(self):
        """Test sorting numbers in descending order."""
        params = {"data": "5,3,8,1", "numeric": True, "order": "desc"}
        result = sort_data(params)
        expected = [8, 5, 3, 1]
        assert json.loads(result) == expected

    def test_sort_text_ascending(self):
        """Test sorting text in ascending order."""
        params = {"data": "zebra,apple,cat", "numeric": False, "order": "asc"}
        result = sort_data(params)
        assert result == "apple, cat, zebra"

    def test_sort_text_descending(self):
        """Test sorting text in descending order."""
        params = {"data": "zebra,apple,cat", "numeric": False, "order": "desc"}
        result = sort_data(params)
        assert result == "zebra, cat, apple"

    def test_sort_case_insensitive_default(self):
        """Test that text sorting is case-insensitive by default."""
        params = {"data": "zebra,Apple,cat"}
        result = sort_data(params)
        assert result == "Apple, cat, zebra"

    def test_sort_case_sensitive(self):
        """Test case-sensitive text sorting."""
        params = {"data": "zebra,Apple,cat", "case_sensitive": True}
        result = sort_data(params)
        assert result == "Apple, cat, zebra"

    def test_sort_json_array(self):
        """Test sorting a JSON array."""
        json_data = '["zebra", "apple", "cat"]'
        params = {"data": json_data}
        result = sort_data(params)
        assert result == "apple, cat, zebra"

    def test_sort_newline_separated(self):
        """Test sorting newline-separated data."""
        params = {"data": "zebra\napple\ncat"}  # Use actual newlines, not escaped
        result = sort_data(params)
        assert result == "apple, cat, zebra"

    def test_sort_mixed_numbers(self):
        """Test sorting mixed integer and float numbers."""
        params = {"data": "5.5,3,8.1,1", "numeric": True}
        result = sort_data(params)
        expected = [1, 3, 5.5, 8.1]
        assert json.loads(result) == expected

    def test_empty_data(self):
        """Test error handling for empty data."""
        params = {"data": ""}
        result = sort_data(params)
        assert "Error: No data provided to sort" in result

    def test_invalid_numeric_data(self):
        """Test error handling for invalid numeric data."""
        params = {"data": "5,abc,3", "numeric": True}
        result = sort_data(params)
        assert "Error: Could not convert data to numbers" in result

    def test_default_parameters(self):
        """Test sorting with minimal parameters (defaults)."""
        params = {"data": "c,a,b"}
        result = sort_data(params)
        assert result == "a, b, c"

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        params = {"data": " zebra , apple , cat "}
        result = sort_data(params)
        assert result == "apple, cat, zebra"

    def test_tool_metadata(self):
        """Test that TOOL_METADATA is properly defined."""
        assert isinstance(TOOL_METADATA, dict)
        assert TOOL_METADATA["name"] == "sort_data"
        assert "description" in TOOL_METADATA
        assert "handler" in TOOL_METADATA
        assert "input_schema" in TOOL_METADATA
        assert TOOL_METADATA["handler"] == sort_data

    def test_tool_metadata_schema(self):
        """Test that the tool schema is valid."""
        schema = TOOL_METADATA["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "data" in schema["required"]

        # Check parameter definitions
        props = schema["properties"]
        assert "data" in props
        assert "order" in props
        assert "numeric" in props
        assert "case_sensitive" in props
