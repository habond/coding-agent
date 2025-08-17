"""Tests for write_file tool."""

import unittest
from unittest.mock import mock_open, patch

from src.tools.write_file import TOOL_METADATA, write_file


class TestWriteFile(unittest.TestCase):
    """Test cases for write_file tool."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_content = "Hello, World!\nThis is test content."

    @patch("src.tools.write_file.os.path.abspath")
    @patch("src.tools.write_file.os.path.exists")
    @patch("src.tools.write_file.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_success(
        self, mock_file_open, mock_makedirs, mock_exists, mock_abspath
    ):
        """Test successful file writing."""
        # Setup mocks
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "test.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True

        params = {"file_path": "test.txt", "content": self.test_content}
        result = write_file(params)

        self.assertIn("Success: Content written to test.txt", result)
        self.assertIn("35 bytes", result)
        mock_file_open.assert_called_once_with(
            "/app/sandbox/test.txt", "w", encoding="utf-8"
        )
        mock_file_open().write.assert_called_once_with(self.test_content)

    @patch("src.tools.write_file.os.path.abspath")
    @patch("src.tools.write_file.os.path.exists")
    @patch("src.tools.write_file.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_append_mode(
        self, mock_file_open, mock_makedirs, mock_exists, mock_abspath
    ):
        """Test file writing in append mode."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "test.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True

        params = {"file_path": "test.txt", "content": self.test_content, "mode": "a"}
        result = write_file(params)

        self.assertIn("Success: Content appended to test.txt", result)
        mock_file_open.assert_called_once_with(
            "/app/sandbox/test.txt", "a", encoding="utf-8"
        )

    @patch("src.tools.write_file.os.path.abspath")
    @patch("src.tools.write_file.os.path.exists")
    @patch("src.tools.write_file.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_create_directory(
        self, mock_file_open, mock_makedirs, mock_exists, mock_abspath
    ):
        """Test creating directory when it doesn't exist."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "subdir/test.txt" else "/app/sandbox"
        )
        mock_exists.return_value = False

        params = {"file_path": "subdir/test.txt", "content": self.test_content}
        result = write_file(params)

        self.assertIn("Success", result)
        mock_makedirs.assert_called_once_with("/app/sandbox/subdir", exist_ok=True)

    def test_write_file_missing_params(self):
        """Test with missing parameters."""
        result = write_file({})
        self.assertEqual(result, "Error: file_path parameter is required")

        result = write_file(None)
        self.assertEqual(result, "Error: file_path parameter is required")

        result = write_file({"file_path": "test.txt"})
        self.assertEqual(result, "Error: content parameter is required")

    def test_write_file_invalid_param_types(self):
        """Test with invalid parameter types."""
        params = {"file_path": 123, "content": "test"}
        result = write_file(params)
        self.assertEqual(result, "Error: file_path must be a string")

        params = {"file_path": "test.txt", "content": 123}
        result = write_file(params)
        self.assertEqual(result, "Error: content must be a string")

    def test_write_file_invalid_mode(self):
        """Test with invalid write mode."""
        params = {"file_path": "test.txt", "content": "test", "mode": "x"}
        result = write_file(params)
        self.assertEqual(
            result, "Error: mode must be 'w' (write/overwrite) or 'a' (append)"
        )

    @patch("src.tools.write_file.os.path.abspath")
    def test_write_file_outside_sandbox(self, mock_abspath):
        """Test access denied for files outside sandbox."""
        mock_abspath.side_effect = (
            lambda x: f"/etc/{x}" if x == "passwd" else "/app/sandbox"
        )

        params = {"file_path": "passwd", "content": "malicious"}
        result = write_file(params)
        self.assertIn("Error: Access denied", result)

    @patch("src.tools.write_file.os.path.abspath")
    @patch("src.tools.write_file.os.path.exists")
    @patch("src.tools.write_file.os.makedirs")
    @patch("builtins.open")
    def test_write_file_permission_error(
        self, mock_file_open, mock_makedirs, mock_exists, mock_abspath
    ):
        """Test permission error handling."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "protected.txt" else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_file_open.side_effect = PermissionError("Permission denied")

        params = {"file_path": "protected.txt", "content": "test"}
        result = write_file(params)
        self.assertIn("Error: Permission denied writing to file", result)

    @patch("src.tools.write_file.os.path.abspath")
    @patch("src.tools.write_file.os.path.exists")
    @patch("src.tools.write_file.os.makedirs")
    def test_write_file_os_error(self, mock_makedirs, mock_exists, mock_abspath):
        """Test OS error handling during directory creation."""
        mock_abspath.side_effect = (
            lambda x: f"/app/sandbox/{x}" if x == "bad/test.txt" else "/app/sandbox"
        )
        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError("Cannot create directory")

        params = {"file_path": "bad/test.txt", "content": "test"}
        result = write_file(params)
        self.assertIn("Error: Failed to create directory or write file", result)

    @patch("src.tools.write_file.os.path.abspath")
    def test_write_file_invalid_path(self, mock_abspath):
        """Test invalid file path handling."""
        mock_abspath.side_effect = Exception("Invalid path")

        params = {"file_path": "invalid\x00path", "content": "test"}
        result = write_file(params)
        self.assertIn("Error: Invalid file path", result)

    def test_tool_metadata(self):
        """Test tool metadata is correctly defined."""
        self.assertEqual(TOOL_METADATA["name"], "write_file")
        self.assertEqual(TOOL_METADATA["handler"], write_file)
        self.assertIn("description", TOOL_METADATA)
        self.assertIn("input_schema", TOOL_METADATA)

        # Test schema structure
        schema = TOOL_METADATA["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("file_path", schema["properties"])
        self.assertIn("content", schema["properties"])
        self.assertIn("mode", schema["properties"])
        self.assertEqual(schema["required"], ["file_path", "content"])

    def test_tool_metadata_schema(self):
        """Test that tool metadata schema is valid."""
        schema = TOOL_METADATA["input_schema"]

        # Verify file_path property
        file_path_prop = schema["properties"]["file_path"]
        self.assertEqual(file_path_prop["type"], "string")
        self.assertIn("description", file_path_prop)

        # Verify content property
        content_prop = schema["properties"]["content"]
        self.assertEqual(content_prop["type"], "string")
        self.assertIn("description", content_prop)

        # Verify mode property
        mode_prop = schema["properties"]["mode"]
        self.assertEqual(mode_prop["type"], "string")
        self.assertEqual(mode_prop["enum"], ["w", "a"])
        self.assertIn("description", mode_prop)
