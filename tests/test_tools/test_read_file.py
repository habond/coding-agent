"""Tests for read_file tool."""

import unittest
from unittest.mock import patch

from src.tools.read_file import TOOL_METADATA, read_file


class TestReadFile(unittest.TestCase):
    """Test cases for read_file tool."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the sandbox directory path
        self.test_content = "Hello, World!\nThis is a test file.\n"

    @patch("src.tools.read_file.os.path.abspath")
    @patch("src.tools.read_file.os.path.exists")
    @patch("src.tools.read_file.os.path.isfile")
    @patch("builtins.open")
    def test_read_file_success(self, mock_open, mock_isfile, mock_exists, mock_abspath):
        """Test successful file reading."""
        # Setup mocks
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "test.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = (
            self.test_content
        )

        params = {"file_path": "test.txt"}
        result = read_file(params)

        self.assertEqual(result, self.test_content)
        mock_open.assert_called_once_with("/app/sandbox/test.txt", encoding="utf-8")

    def test_read_file_missing_params(self):
        """Test with missing parameters."""
        result = read_file({})
        self.assertEqual(result, "Error: file_path parameter is required")

        result = read_file(None)
        self.assertEqual(result, "Error: file_path parameter is required")

    def test_read_file_invalid_path_type(self):
        """Test with invalid path type."""
        params = {"file_path": 123}
        result = read_file(params)
        self.assertEqual(result, "Error: file_path must be a string")

    @patch("src.tools.read_file.os.path.abspath")
    def test_read_file_outside_sandbox(self, mock_abspath):
        """Test access denied for files outside sandbox."""
        mock_abspath.side_effect = (
            lambda x: f"/etc/{x}" if x == "passwd" else "/app/sandbox"
        )

        params = {"file_path": "passwd"}
        result = read_file(params)
        self.assertIn("Error: Access denied", result)

    @patch("src.tools.read_file.os.path.abspath")
    @patch("src.tools.read_file.os.path.exists")
    def test_read_file_not_found(self, mock_exists, mock_abspath):
        """Test file not found error."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "nonexistent.txt" else "/app/sandbox"
        )
        mock_exists.return_value = False

        params = {"file_path": "nonexistent.txt"}
        result = read_file(params)
        self.assertIn("Error: File not found", result)

    @patch("src.tools.read_file.os.path.abspath")
    @patch("src.tools.read_file.os.path.exists")
    @patch("src.tools.read_file.os.path.isfile")
    def test_read_file_is_directory(self, mock_isfile, mock_exists, mock_abspath):
        """Test error when path is a directory."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "subdir" else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isfile.return_value = False

        params = {"file_path": "subdir"}
        result = read_file(params)
        self.assertIn("Error: Path is not a file", result)

    @patch("src.tools.read_file.os.path.abspath")
    @patch("src.tools.read_file.os.path.exists")
    @patch("src.tools.read_file.os.path.isfile")
    @patch("builtins.open")
    def test_read_file_permission_error(
        self, mock_open, mock_isfile, mock_exists, mock_abspath
    ):
        """Test permission error handling."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "protected.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.side_effect = PermissionError("Permission denied")

        params = {"file_path": "protected.txt"}
        result = read_file(params)
        self.assertIn("Error: Permission denied", result)

    @patch("src.tools.read_file.os.path.abspath")
    @patch("src.tools.read_file.os.path.exists")
    @patch("src.tools.read_file.os.path.isfile")
    @patch("builtins.open")
    def test_read_file_unicode_error(
        self, mock_open, mock_isfile, mock_exists, mock_abspath
    ):
        """Test Unicode decode error handling."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "binary.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid start byte"
        )

        params = {"file_path": "binary.txt"}
        result = read_file(params)
        self.assertIn("Error: Cannot decode file as UTF-8", result)

    def test_tool_metadata(self):
        """Test tool metadata is correctly defined."""
        self.assertEqual(TOOL_METADATA["name"], "read_file")
        self.assertEqual(TOOL_METADATA["handler"], read_file)
        self.assertIn("description", TOOL_METADATA)
        self.assertIn("input_schema", TOOL_METADATA)

        # Test schema structure
        schema = TOOL_METADATA["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("file_path", schema["properties"])
        self.assertEqual(schema["required"], ["file_path"])

    def test_tool_metadata_schema(self):
        """Test that tool metadata schema is valid."""
        schema = TOOL_METADATA["input_schema"]

        # Verify file_path property
        file_path_prop = schema["properties"]["file_path"]
        self.assertEqual(file_path_prop["type"], "string")
        self.assertIn("description", file_path_prop)
