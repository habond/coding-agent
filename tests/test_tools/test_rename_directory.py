"""Tests for rename_directory tool."""

import unittest
from unittest.mock import patch

from tools.rename_directory import rename_directory


class TestRenameDirectory(unittest.TestCase):
    """Test cases for rename_directory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox_dir = "/app/sandbox"

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_rename_directory_success(
        self, mock_move, mock_makedirs, mock_isdir, mock_exists
    ):
        """Test successful directory rename."""
        # Mock existence checks
        mock_exists.side_effect = [
            True,
            False,
            True,
        ]  # old exists, new doesn't, parent exists
        mock_isdir.return_value = True

        params = {
            "old_path": "/app/sandbox/olddir",
            "new_path": "/app/sandbox/newdir",
        }
        result = rename_directory(params)

        self.assertIn("Success", result)
        self.assertIn("Renamed directory 'olddir' to 'newdir'", result)
        mock_move.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_rename_directory_with_parent_creation(
        self, mock_move, mock_makedirs, mock_isdir, mock_exists
    ):
        """Test renaming directory to a path that needs parent creation."""
        # Mock existence checks
        mock_exists.side_effect = [
            True,
            False,
            False,
        ]  # old exists, new doesn't, parent doesn't exist
        mock_isdir.return_value = True

        params = {
            "old_path": "/app/sandbox/olddir",
            "new_path": "/app/sandbox/parent/newdir",
        }
        result = rename_directory(params)

        self.assertIn("Success", result)
        mock_makedirs.assert_called_once()
        mock_move.assert_called_once()

    @patch("os.path.exists")
    def test_rename_directory_not_found(self, mock_exists):
        """Test error when source directory doesn't exist."""
        mock_exists.return_value = False

        params = {
            "old_path": "/app/sandbox/nonexistent",
            "new_path": "/app/sandbox/newdir",
        }
        result = rename_directory(params)

        self.assertIn("Error: Directory not found", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_rename_directory_source_not_dir(self, mock_isdir, mock_exists):
        """Test error when source is not a directory."""
        mock_exists.return_value = True
        mock_isdir.return_value = False

        params = {
            "old_path": "/app/sandbox/file.txt",
            "new_path": "/app/sandbox/newdir",
        }
        result = rename_directory(params)

        self.assertIn("Error: Path is not a directory", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_rename_directory_destination_exists(self, mock_isdir, mock_exists):
        """Test error when destination already exists."""
        mock_exists.side_effect = [True, True]  # both exist
        mock_isdir.return_value = True

        params = {
            "old_path": "/app/sandbox/olddir",
            "new_path": "/app/sandbox/existing",
        }
        result = rename_directory(params)

        self.assertIn("Error: Destination already exists", result)

    def test_rename_directory_missing_old_path(self):
        """Test error when old_path is missing."""
        params = {"new_path": "/app/sandbox/newdir"}
        result = rename_directory(params)
        self.assertEqual(result, "Error: old_path parameter is required")

    def test_rename_directory_missing_new_path(self):
        """Test error when new_path is missing."""
        params = {"old_path": "/app/sandbox/olddir"}
        result = rename_directory(params)
        self.assertEqual(result, "Error: new_path parameter is required")

    def test_rename_directory_invalid_types(self):
        """Test type validation for parameters."""
        # Invalid old_path type
        params = {"old_path": 123, "new_path": "/app/sandbox/newdir"}
        result = rename_directory(params)
        self.assertEqual(result, "Error: old_path must be a string")

        # Invalid new_path type
        params = {"old_path": "/app/sandbox/olddir", "new_path": 456}
        result = rename_directory(params)
        self.assertEqual(result, "Error: new_path must be a string")

    def test_rename_directory_outside_sandbox(self):
        """Test security checks for paths outside sandbox."""
        # Source outside sandbox
        params = {"old_path": "/etc/dir", "new_path": "/app/sandbox/newdir"}
        result = rename_directory(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("Source directory must be within", result)

        # Destination outside sandbox
        params = {"old_path": "/app/sandbox/olddir", "new_path": "/etc/newdir"}
        result = rename_directory(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("Destination must be within", result)

    def test_rename_sandbox_root(self):
        """Test that sandbox root cannot be renamed."""
        params = {"old_path": "/app/sandbox", "new_path": "/app/sandbox2"}
        result = rename_directory(params)
        # Either error message is acceptable since both protect the sandbox root
        self.assertTrue(
            "Error: Cannot rename the sandbox root" in result
            or "Error: Access denied" in result
        )

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_rename_directory_permission_error(
        self, mock_move, mock_makedirs, mock_isdir, mock_exists
    ):
        """Test handling of permission errors."""
        mock_exists.side_effect = [
            True,
            False,
            True,
        ]  # old exists, new doesn't, parent exists
        mock_isdir.return_value = True
        mock_move.side_effect = PermissionError("Access denied")

        params = {
            "old_path": "/app/sandbox/olddir",
            "new_path": "/app/sandbox/newdir",
        }
        result = rename_directory(params)
        self.assertIn("Error: Permission denied", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_rename_directory_os_error(
        self, mock_move, mock_makedirs, mock_isdir, mock_exists
    ):
        """Test handling of OS errors."""
        mock_exists.side_effect = [
            True,
            False,
            True,
        ]  # old exists, new doesn't, parent exists
        mock_isdir.return_value = True
        mock_move.side_effect = OSError("Cross-device link")

        params = {
            "old_path": "/app/sandbox/olddir",
            "new_path": "/app/sandbox/newdir",
        }
        result = rename_directory(params)
        self.assertIn("Error: Failed to rename directory", result)


if __name__ == "__main__":
    unittest.main()
