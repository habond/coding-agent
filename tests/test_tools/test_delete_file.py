"""Tests for delete_file tool."""

import unittest
from unittest.mock import patch

from tools.delete_file import TOOL_METADATA, delete_file


class TestDeleteFile(unittest.TestCase):
    """Test cases for delete_file tool."""

    def test_tool_metadata(self) -> None:
        """Test that tool metadata is properly defined."""
        self.assertEqual(TOOL_METADATA["name"], "delete_file")
        self.assertEqual(TOOL_METADATA["handler"], delete_file)
        self.assertIn("description", TOOL_METADATA)
        self.assertIn("input_schema", TOOL_METADATA)

    def test_tool_metadata_schema(self) -> None:
        """Test that the input schema is properly structured."""
        schema = TOOL_METADATA["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        self.assertEqual(set(schema["required"]), {"file_path"})

        properties = schema["properties"]
        self.assertIn("file_path", properties)
        self.assertEqual(properties["file_path"]["type"], "string")

    def test_delete_file_missing_params(self) -> None:
        """Test delete_file with missing parameters."""
        # Missing file_path
        result = delete_file({})
        self.assertIn("Error: file_path parameter is required", result)

        # None params
        result = delete_file(None)
        self.assertIn("Error: file_path parameter is required", result)

    def test_delete_file_invalid_param_types(self) -> None:
        """Test delete_file with invalid parameter types."""
        # Non-string file_path
        result = delete_file({"file_path": 123})
        self.assertIn("Error: file_path must be a string", result)

        # List as file_path
        result = delete_file({"file_path": ["/app/sandbox/test.txt"]})
        self.assertIn("Error: file_path must be a string", result)

    def test_delete_file_outside_sandbox(self) -> None:
        """Test delete_file with paths outside sandbox directory."""
        # Path outside sandbox
        result = delete_file({"file_path": "/etc/passwd"})
        self.assertIn("Error: file_path must be within sandbox directory", result)

        # Path trying to escape sandbox
        result = delete_file({"file_path": "/app/sandbox/../../../etc/passwd"})
        self.assertIn("Error: file_path must be within sandbox directory", result)

        # Root path
        result = delete_file({"file_path": "/"})
        self.assertIn("Error: file_path must be within sandbox directory", result)

    def test_delete_file_invalid_path(self) -> None:
        """Test delete_file with invalid file paths."""
        # Test with invalid characters (mocked to raise OSError)
        with patch("os.path.abspath", side_effect=OSError("Invalid path")):
            result = delete_file({"file_path": "/app/sandbox/test.txt"})
            self.assertIn("Error: Invalid file path", result)

        # Test with ValueError
        with patch("os.path.abspath", side_effect=ValueError("Invalid value")):
            result = delete_file({"file_path": "/app/sandbox/test.txt"})
            self.assertIn("Error: Invalid file path", result)

    @patch("os.path.exists")
    def test_delete_file_not_found(self, mock_exists):
        """Test delete_file when file doesn't exist."""
        mock_exists.return_value = False

        result = delete_file({"file_path": "/app/sandbox/nonexistent.txt"})
        self.assertIn("Error: File not found", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_delete_file_is_directory(self, mock_isfile, mock_exists):
        """Test delete_file when path is a directory."""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        result = delete_file({"file_path": "/app/sandbox/somedir"})
        self.assertIn("Error: Path is not a file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove", side_effect=PermissionError("Permission denied"))
    def test_delete_file_permission_error(self, mock_remove, mock_isfile, mock_exists):
        """Test delete_file with permission error."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/test.txt"})
        self.assertIn("Error: Permission denied deleting file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove", side_effect=OSError("Device busy"))
    def test_delete_file_os_error(self, mock_remove, mock_isfile, mock_exists):
        """Test delete_file with OS error."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/test.txt"})
        self.assertIn("Error: Failed to delete file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove", side_effect=Exception("Unexpected error"))
    def test_delete_file_unexpected_error(self, mock_remove, mock_isfile, mock_exists):
        """Test delete_file with unexpected error."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/test.txt"})
        self.assertIn("Error: Unexpected error during deletion", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_file_success(self, mock_remove, mock_isfile, mock_exists):
        """Test successful file deletion."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/test.txt"})

        # Should call os.remove
        mock_remove.assert_called_once()
        self.assertIn("Success: Deleted file", result)
        self.assertIn("test.txt", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_file_success_nested_path(
        self, mock_remove, mock_isfile, mock_exists
    ):
        """Test successful file deletion with nested path."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/subdir/nested/test.txt"})

        # Should call os.remove
        mock_remove.assert_called_once()
        self.assertIn("Success: Deleted file", result)
        self.assertIn("subdir/nested/test.txt", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_file_success_relative_display(
        self, mock_remove, mock_isfile, mock_exists
    ):
        """Test that success message shows relative path."""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        result = delete_file({"file_path": "/app/sandbox/docs/readme.txt"})

        # Should call os.remove
        mock_remove.assert_called_once()
        self.assertIn("Success: Deleted file 'docs/readme.txt'", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_delete_file_sandbox_root_protection(self, mock_isfile, mock_exists):
        """Test that sandbox root directory is protected."""
        mock_exists.return_value = True
        mock_isfile.return_value = False  # Directory, not a file

        # Try to delete sandbox directory itself
        result = delete_file({"file_path": "/app/sandbox"})
        self.assertIn("Error: Path is not a file", result)


if __name__ == "__main__":
    unittest.main()
