"""Tests for create_directory tool."""

import unittest
from unittest.mock import patch

from tools.create_directory import create_directory


class TestCreateDirectory(unittest.TestCase):
    """Test cases for create_directory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox_dir = "/app/sandbox"

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_directory_success(self, mock_makedirs, mock_exists):
        """Test successful directory creation."""
        mock_exists.return_value = False

        params = {"directory_path": "/app/sandbox/newdir"}
        result = create_directory(params)

        self.assertIn("Success", result)
        self.assertIn("Created directory 'newdir'", result)
        mock_makedirs.assert_called_once()

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_nested_directory_success(self, mock_makedirs, mock_exists):
        """Test successful nested directory creation."""
        mock_exists.return_value = False

        params = {"directory_path": "/app/sandbox/parent/child/grandchild"}
        result = create_directory(params)

        self.assertIn("Success", result)
        self.assertIn("parent/child/grandchild", result)
        mock_makedirs.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_create_directory_already_exists(self, mock_isdir, mock_exists):
        """Test error when directory already exists."""
        mock_exists.return_value = True
        mock_isdir.return_value = True

        params = {"directory_path": "/app/sandbox/existing"}
        result = create_directory(params)

        self.assertIn("Error", result)
        self.assertIn("already exists", result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_create_directory_path_exists_not_dir(self, mock_isdir, mock_exists):
        """Test error when path exists but is not a directory."""
        mock_exists.return_value = True
        mock_isdir.return_value = False

        params = {"directory_path": "/app/sandbox/file.txt"}
        result = create_directory(params)

        self.assertIn("Error", result)
        self.assertIn("is not a directory", result)

    def test_create_directory_missing_params(self):
        """Test error when directory_path is missing."""
        params = {}
        result = create_directory(params)
        self.assertEqual(result, "Error: directory_path parameter is required")

    def test_create_directory_invalid_type(self):
        """Test type validation for directory_path."""
        params = {"directory_path": 123}
        result = create_directory(params)
        self.assertEqual(result, "Error: directory_path must be a string")

    def test_create_directory_outside_sandbox(self):
        """Test security check prevents creating directories outside sandbox."""
        params = {"directory_path": "/etc/newdir"}
        result = create_directory(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("/app/sandbox", result)

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_directory_permission_error(self, mock_makedirs, mock_exists):
        """Test handling of permission errors."""
        mock_exists.return_value = False
        mock_makedirs.side_effect = PermissionError("Access denied")

        params = {"directory_path": "/app/sandbox/protected"}
        result = create_directory(params)
        self.assertIn("Error: Permission denied", result)

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_directory_os_error(self, mock_makedirs, mock_exists):
        """Test handling of OS errors."""
        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError("Disk full")

        params = {"directory_path": "/app/sandbox/newdir"}
        result = create_directory(params)
        self.assertIn("Error: Failed to create directory", result)
        self.assertIn("Disk full", result)


if __name__ == "__main__":
    unittest.main()
