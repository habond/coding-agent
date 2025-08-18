"""Tests for rename_file tool."""

import unittest
from unittest.mock import patch

from tools.rename_file import TOOL_METADATA, rename_file


class TestRenameFile(unittest.TestCase):
    """Test cases for rename_file tool."""

    def test_tool_metadata(self) -> None:
        """Test that tool metadata is properly defined."""
        self.assertEqual(TOOL_METADATA["name"], "rename_file")
        self.assertEqual(TOOL_METADATA["handler"], rename_file)
        self.assertIn("description", TOOL_METADATA)
        self.assertIn("input_schema", TOOL_METADATA)

    def test_tool_metadata_schema(self) -> None:
        """Test that the input schema is properly structured."""
        schema = TOOL_METADATA["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        self.assertEqual(set(schema["required"]), {"old_path", "new_path"})

        properties = schema["properties"]
        self.assertIn("old_path", properties)
        self.assertIn("new_path", properties)
        self.assertEqual(properties["old_path"]["type"], "string")
        self.assertEqual(properties["new_path"]["type"], "string")

    def test_rename_file_missing_params(self) -> None:
        """Test rename_file with missing parameters."""
        # Missing old_path
        result = rename_file({"new_path": "/app/sandbox/new.txt"})
        self.assertIn("Error: old_path parameter is required", result)

        # Missing new_path
        result = rename_file({"old_path": "/app/sandbox/old.txt"})
        self.assertIn("Error: new_path parameter is required", result)

        # Empty params
        result = rename_file({})
        self.assertIn("Error: old_path parameter is required", result)

        # None params
        result = rename_file(None)
        self.assertIn("Error: old_path parameter is required", result)

    def test_rename_file_invalid_param_types(self) -> None:
        """Test rename_file with invalid parameter types."""
        # Non-string old_path
        result = rename_file({"old_path": 123, "new_path": "/app/sandbox/new.txt"})
        self.assertIn("Error: old_path must be a string", result)

        # Non-string new_path
        result = rename_file({"old_path": "/app/sandbox/old.txt", "new_path": 456})
        self.assertIn("Error: new_path must be a string", result)

    def test_rename_file_outside_sandbox(self) -> None:
        """Test rename_file with paths outside sandbox directory."""
        # Old path outside sandbox
        result = rename_file(
            {"old_path": "/etc/passwd", "new_path": "/app/sandbox/new.txt"}
        )
        self.assertIn("Error: old_path must be within sandbox directory", result)

        # New path outside sandbox
        result = rename_file(
            {"old_path": "/app/sandbox/old.txt", "new_path": "/etc/new.txt"}
        )
        self.assertIn("Error: new_path must be within sandbox directory", result)

        # Both paths outside sandbox
        result = rename_file({"old_path": "/etc/old.txt", "new_path": "/etc/new.txt"})
        self.assertIn("Error: old_path must be within sandbox directory", result)

    def test_rename_file_invalid_path(self) -> None:
        """Test rename_file with invalid file paths."""
        # Test with invalid characters (mocked to raise OSError)
        with patch("os.path.abspath", side_effect=OSError("Invalid path")):
            result = rename_file(
                {"old_path": "/app/sandbox/old.txt", "new_path": "/app/sandbox/new.txt"}
            )
            self.assertIn("Error: Invalid file path", result)

    @patch("os.path.exists")
    def test_rename_file_not_found(self, mock_exists):
        """Test rename_file when source file doesn't exist."""
        mock_exists.return_value = False

        result = rename_file(
            {
                "old_path": "/app/sandbox/nonexistent.txt",
                "new_path": "/app/sandbox/new.txt",
            }
        )
        self.assertIn("Error: Source file not found", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_rename_file_is_directory(self, mock_isfile, mock_exists):
        """Test rename_file when source path is a directory."""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        result = rename_file(
            {"old_path": "/app/sandbox/somedir", "new_path": "/app/sandbox/new.txt"}
        )
        self.assertIn("Error: Source path is not a file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_rename_file_destination_exists(self, mock_isfile, mock_exists):
        """Test rename_file when destination already exists."""

        def mock_exists_side_effect(path):
            return True  # Both source and destination exist

        mock_exists.side_effect = mock_exists_side_effect
        mock_isfile.return_value = True

        result = rename_file(
            {
                "old_path": "/app/sandbox/old.txt",
                "new_path": "/app/sandbox/existing.txt",
            }
        )
        self.assertIn("Error: Destination already exists", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.makedirs")  # Mock makedirs to avoid directory creation
    @patch("os.rename", side_effect=PermissionError("Permission denied"))
    def test_rename_file_permission_error(
        self, mock_rename, mock_makedirs, mock_isfile, mock_exists
    ):
        """Test rename_file with permission error."""

        def mock_exists_side_effect(path):
            # Source exists, destination doesn't
            return "/old.txt" in path

        mock_exists.side_effect = mock_exists_side_effect
        mock_isfile.return_value = True

        result = rename_file(
            {"old_path": "/app/sandbox/old.txt", "new_path": "/app/sandbox/new.txt"}
        )
        self.assertIn("Error: Permission denied renaming file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("os.rename", side_effect=OSError("Disk full"))
    def test_rename_file_os_error(
        self, mock_rename, mock_makedirs, mock_isfile, mock_exists
    ):
        """Test rename_file with OS error."""

        def mock_exists_side_effect(path):
            # Source exists, destination doesn't
            return "/old.txt" in path

        mock_exists.side_effect = mock_exists_side_effect
        mock_isfile.return_value = True

        result = rename_file(
            {"old_path": "/app/sandbox/old.txt", "new_path": "/app/sandbox/new.txt"}
        )
        self.assertIn("Error: Failed to rename file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("os.rename")
    def test_rename_file_success(
        self, mock_rename, mock_makedirs, mock_isfile, mock_exists
    ):
        """Test successful file rename."""

        def mock_exists_side_effect(path):
            # Source exists, destination and its directory don't
            return "/old.txt" in path

        mock_exists.side_effect = mock_exists_side_effect
        mock_isfile.return_value = True

        result = rename_file(
            {
                "old_path": "/app/sandbox/old.txt",
                "new_path": "/app/sandbox/subdir/new.txt",
            }
        )

        # Should create directory and rename file
        mock_makedirs.assert_called_once()
        mock_rename.assert_called_once()
        self.assertIn("Success: Renamed", result)
        self.assertIn("old.txt", result)
        self.assertIn("subdir/new.txt", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.rename")
    def test_rename_file_success_simple(self, mock_rename, mock_isfile, mock_exists):
        """Test successful file rename without directory creation."""

        def mock_exists_side_effect(path):
            # Source exists, destination doesn't, but destination directory exists
            if "/old.txt" in path:
                return True
            elif "/new.txt" in path:
                return False
            elif "/sandbox" in path and "/new.txt" not in path:
                return True  # Directory exists
            return False

        mock_exists.side_effect = mock_exists_side_effect
        mock_isfile.return_value = True

        result = rename_file(
            {"old_path": "/app/sandbox/old.txt", "new_path": "/app/sandbox/new.txt"}
        )

        mock_rename.assert_called_once()
        self.assertIn("Success: Renamed", result)
        self.assertIn("old.txt", result)
        self.assertIn("new.txt", result)


if __name__ == "__main__":
    unittest.main()
