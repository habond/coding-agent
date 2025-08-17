"""Tests for get_current_time tool."""

from tools.get_current_time import TOOL_METADATA, get_current_time


class TestGetCurrentTime:
    """Test cases for get_current_time tool."""

    def test_get_current_time_returns_string(self):
        """Test that get_current_time returns a string."""
        result = get_current_time()
        assert isinstance(result, str)

    def test_get_current_time_format(self):
        """Test that the returned time has the expected format."""
        result = get_current_time()
        # Should match format: YYYY-MM-DD HH:MM:SS timezone
        parts = result.split()
        assert len(parts) >= 2, f"Expected at least 2 parts, got: {result}"

        # Check date format YYYY-MM-DD
        date_part = parts[0]
        assert len(date_part) == 10, f"Date part should be 10 chars, got: {date_part}"
        assert date_part.count("-") == 2, f"Date should have 2 dashes, got: {date_part}"

        # Check time format HH:MM:SS
        time_part = parts[1]
        assert len(time_part) == 8, f"Time part should be 8 chars, got: {time_part}"
        assert time_part.count(":") == 2, f"Time should have 2 colons, got: {time_part}"

    def test_get_current_time_with_params(self):
        """Test that get_current_time works with parameters (even though they're ignored)."""
        result = get_current_time({"some": "param"})
        assert isinstance(result, str)

    def test_get_current_time_without_params(self):
        """Test that get_current_time works without parameters."""
        result = get_current_time()
        assert isinstance(result, str)

    def test_tool_metadata(self):
        """Test that TOOL_METADATA is properly defined."""
        assert isinstance(TOOL_METADATA, dict)
        assert TOOL_METADATA["name"] == "get_current_time"
        assert "description" in TOOL_METADATA
        assert "handler" in TOOL_METADATA
        assert "input_schema" in TOOL_METADATA
        assert TOOL_METADATA["handler"] == get_current_time

    def test_tool_metadata_schema(self):
        """Test that the tool schema is valid."""
        schema = TOOL_METADATA["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert schema["required"] == []
