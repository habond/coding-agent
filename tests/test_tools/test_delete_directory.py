"""Tests for delete_directory tool."""

import unittest
from unittest.mock import patch

from tools.delete_directory import delete_directory


class TestDeleteDirectory(unittest.TestCase):
    """Test cases for delete_directory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox_dir = "/app/sandbox"

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("os.rmdir")
    def test_delete_empty_directory_success(
        self, mock_rmdir, mock_listdir, mock_isdir, mock_exists
    ):
        """Test successful deletion of empty directory."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = []  # Empty directory

        params = {"directory_path": "/app/sandbox/emptydir"}
        result = delete_directory(params)

        self.assertIn("Success", result)
        self.assertIn("Deleted directory 'emptydir'", result)
        mock_rmdir.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("shutil.rmtree")
    def test_delete_directory_with_force(
        self, mock_rmtree, mock_listdir, mock_isdir, mock_exists
    ):
        """Test deletion of non-empty directory with force=True."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt"]  # Non-empty

        params = {"directory_path": "/app/sandbox/fulldir", "force": True}
        result = delete_directory(params)

        self.assertIn("Success", result)
        self.assertIn("Deleted directory 'fulldir'", result)
        mock_rmtree.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    def test_delete_non_empty_without_force(
        self, mock_listdir, mock_isdir, mock_exists
    ):
        """Test error when trying to delete non-empty directory without force."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.txt"]  # Non-empty

        params = {"directory_path": "/app/sandbox/fulldir"}
        result = delete_directory(params)

        self.assertIn("Error", result)
        self.assertIn("Directory is not empty", result)
        self.assertIn("force=true", result)

    @patch("os.path.exists")
    def test_delete_directory_not_found(self, mock_exists):
        """Test error when directory doesn't exist."""
        mock_exists.return_value = False

        params = {"directory_path": "/app/sandbox/nonexistent"}
        result = delete_directory(params)

        self.assertIn("Error: Directory not found", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_delete_directory_not_dir(self, mock_isdir, mock_exists):
        """Test error when path is not a directory."""
        mock_exists.return_value = True
        mock_isdir.return_value = False

        params = {"directory_path": "/app/sandbox/file.txt"}
        result = delete_directory(params)

        self.assertIn("Error: Path is not a directory", result)

    def test_delete_directory_missing_params(self):
        """Test error when directory_path is missing."""
        params = {}
        result = delete_directory(params)
        self.assertEqual(result, "Error: directory_path parameter is required")

    def test_delete_directory_invalid_types(self):
        """Test type validation for parameters."""
        # Invalid directory_path type
        params = {"directory_path": 123}
        result = delete_directory(params)
        self.assertEqual(result, "Error: directory_path must be a string")

        # Invalid force type
        params = {"directory_path": "/app/sandbox/dir", "force": "yes"}
        result = delete_directory(params)
        self.assertEqual(result, "Error: force must be a boolean")

    def test_delete_directory_outside_sandbox(self):
        """Test security check prevents deleting directories outside sandbox."""
        params = {"directory_path": "/etc/dir"}
        result = delete_directory(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("/app/sandbox", result)

    def test_delete_sandbox_root(self):
        """Test that sandbox root cannot be deleted."""
        params = {"directory_path": "/app/sandbox"}
        result = delete_directory(params)
        self.assertIn("Error: Cannot delete the sandbox root", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("os.rmdir")
    def test_delete_directory_permission_error(
        self, mock_rmdir, mock_listdir, mock_isdir, mock_exists
    ):
        """Test handling of permission errors."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        mock_rmdir.side_effect = PermissionError("Access denied")

        params = {"directory_path": "/app/sandbox/protected"}
        result = delete_directory(params)
        self.assertIn("Error: Permission denied", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("shutil.rmtree")
    def test_delete_directory_os_error(
        self, mock_rmtree, mock_listdir, mock_isdir, mock_exists
    ):
        """Test handling of OS errors."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file.txt"]
        mock_rmtree.side_effect = OSError("Device busy")

        params = {"directory_path": "/app/sandbox/busydir", "force": True}
        result = delete_directory(params)
        self.assertIn("Error: Failed to delete directory", result)
        self.assertIn("Device busy", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("os.rmdir")
    def test_delete_nested_directory(
        self, mock_rmdir, mock_listdir, mock_isdir, mock_exists
    ):
        """Test deletion of nested directory path."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = []

        params = {"directory_path": "/app/sandbox/parent/child/grandchild"}
        result = delete_directory(params)

        self.assertIn("Success", result)
        self.assertIn("parent/child/grandchild", result)
        mock_rmdir.assert_called_once()


if __name__ == "__main__":
    unittest.main()
