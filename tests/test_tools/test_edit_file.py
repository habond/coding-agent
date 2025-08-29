"""Tests for edit_file tool."""

import unittest
from unittest.mock import Mock, patch

from tools.edit_file import edit_file


class TestEditFile(unittest.TestCase):
    """Test cases for edit_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox_dir = "/app/sandbox"

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_edit_file_success_single_replacement(
        self, mock_open, mock_isfile, mock_exists
    ):
        """Test successful single string replacement."""
        # Configure mocks
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Mock file content
        mock_file = Mock()
        mock_file.read.return_value = "Hello world! Hello again!"
        mock_open.return_value.__enter__.return_value = mock_file

        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": "Hello",
            "new_string": "Hi",
            "replace_all": False,
        }

        result = edit_file(params)

        self.assertIn("Success", result)
        self.assertIn("1 occurrence(s)", result)

        # Verify the file was written with the correct content
        write_calls = [call for call in mock_file.method_calls if call[0] == "write"]
        self.assertEqual(len(write_calls), 1)
        written_content = write_calls[0][1][0]
        self.assertEqual(written_content, "Hi world! Hello again!")

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_edit_file_success_replace_all(self, mock_open, mock_isfile, mock_exists):
        """Test successful replacement of all occurrences."""
        # Configure mocks
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Mock file content
        mock_file = Mock()
        mock_file.read.return_value = "Hello world! Hello again!"
        mock_open.return_value.__enter__.return_value = mock_file

        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": "Hello",
            "new_string": "Hi",
            "replace_all": True,
        }

        result = edit_file(params)

        self.assertIn("Success", result)
        self.assertIn("2 occurrence(s)", result)

        # Verify the file was written with the correct content
        write_calls = [call for call in mock_file.method_calls if call[0] == "write"]
        self.assertEqual(len(write_calls), 1)
        written_content = write_calls[0][1][0]
        self.assertEqual(written_content, "Hi world! Hi again!")

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_edit_file_string_not_found(self, mock_open, mock_isfile, mock_exists):
        """Test when old_string is not found in file."""
        # Configure mocks
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Mock file content
        mock_file = Mock()
        mock_file.read.return_value = "Hello world!"
        mock_open.return_value.__enter__.return_value = mock_file

        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": "Goodbye",
            "new_string": "Hi",
        }

        result = edit_file(params)

        self.assertIn("Error", result)
        self.assertIn("not found", result)

    def test_edit_file_missing_file_path(self):
        """Test error when file_path is missing."""
        params = {"old_string": "test", "new_string": "replacement"}
        result = edit_file(params)
        self.assertEqual(result, "Error: file_path parameter is required")

    def test_edit_file_missing_old_string(self):
        """Test error when old_string is missing."""
        params = {"file_path": "/app/sandbox/test.txt", "new_string": "replacement"}
        result = edit_file(params)
        self.assertEqual(result, "Error: old_string parameter is required")

    def test_edit_file_missing_new_string(self):
        """Test error when new_string is missing."""
        params = {"file_path": "/app/sandbox/test.txt", "old_string": "test"}
        result = edit_file(params)
        self.assertEqual(result, "Error: new_string parameter is required")

    def test_edit_file_outside_sandbox(self):
        """Test security check prevents editing files outside sandbox."""
        params = {
            "file_path": "/etc/passwd",
            "old_string": "root",
            "new_string": "hacker",
        }
        result = edit_file(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("/app/sandbox", result)

    @patch("os.path.exists")
    def test_edit_file_not_found(self, mock_exists):
        """Test error when file doesn't exist."""
        mock_exists.return_value = False

        params = {
            "file_path": "/app/sandbox/nonexistent.txt",
            "old_string": "test",
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertIn("Error: File not found", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_edit_file_is_directory(self, mock_isfile, mock_exists):
        """Test error when path is a directory."""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        params = {
            "file_path": "/app/sandbox/somedir",
            "old_string": "test",
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertIn("Error: Path is not a file", result)

    def test_edit_file_invalid_types(self):
        """Test type validation for parameters."""
        # Invalid file_path type
        params = {
            "file_path": 123,
            "old_string": "test",
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertEqual(result, "Error: file_path must be a string")

        # Invalid old_string type
        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": 123,
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertEqual(result, "Error: old_string must be a string")

        # Invalid new_string type
        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": "test",
            "new_string": 123,
        }
        result = edit_file(params)
        self.assertEqual(result, "Error: new_string must be a string")

        # Invalid replace_all type
        params = {
            "file_path": "/app/sandbox/test.txt",
            "old_string": "test",
            "new_string": "replacement",
            "replace_all": "true",
        }
        result = edit_file(params)
        self.assertEqual(result, "Error: replace_all must be a boolean")

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_edit_file_permission_error(self, mock_open, mock_isfile, mock_exists):
        """Test handling of permission errors."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.side_effect = PermissionError("Access denied")

        params = {
            "file_path": "/app/sandbox/protected.txt",
            "old_string": "test",
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertIn("Error: Permission denied", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open")
    def test_edit_file_unicode_error(self, mock_open, mock_isfile, mock_exists):
        """Test handling of Unicode decode errors."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid start byte"
        )

        params = {
            "file_path": "/app/sandbox/binary.dat",
            "old_string": "test",
            "new_string": "replacement",
        }
        result = edit_file(params)
        self.assertIn("Error: Cannot decode file as UTF-8", result)


if __name__ == "__main__":
    unittest.main()
