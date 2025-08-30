"""Tests for move_file tool."""

import unittest
from unittest.mock import patch

from tools.move_file import move_file


class TestMoveFile(unittest.TestCase):
    """Test cases for move_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox_dir = "/app/sandbox"

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_move_file_success(
        self, mock_move, mock_makedirs, mock_isdir, mock_isfile, mock_exists
    ):
        """Test successful file move to existing directory."""
        # Mock existence checks: source exists, dest file doesn't, dest dir exists
        mock_exists.side_effect = [True, False, True]
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)

        self.assertIn("Success", result)
        self.assertIn("Moved file 'file.txt' to 'newdir/file.txt'", result)
        mock_move.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_move_file_with_rename(
        self, mock_move, mock_makedirs, mock_isdir, mock_isfile, mock_exists
    ):
        """Test moving file with a new name."""
        # Mock existence checks: source exists, dest file doesn't, dest dir exists
        mock_exists.side_effect = [True, False, True]
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
            "new_name": "renamed.txt",
        }
        result = move_file(params)

        self.assertIn("Success", result)
        self.assertIn("Moved file 'file.txt' to 'newdir/renamed.txt'", result)
        mock_move.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_move_file_create_destination_dir(
        self, mock_move, mock_makedirs, mock_isfile, mock_exists
    ):
        """Test moving file when destination directory doesn't exist."""
        # Mock existence checks: source exists, dest file doesn't, dest dir doesn't exist
        mock_exists.side_effect = [True, False, False]
        mock_isfile.return_value = True

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)

        self.assertIn("Success", result)
        mock_makedirs.assert_called_once()
        mock_move.assert_called_once()

    @patch("os.path.exists")
    def test_move_file_source_not_found(self, mock_exists):
        """Test error when source file doesn't exist."""
        mock_exists.return_value = False

        params = {
            "source_path": "/app/sandbox/nonexistent.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)

        self.assertIn("Error: File not found", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_move_file_source_not_file(self, mock_isfile, mock_exists):
        """Test error when source is not a file."""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        params = {
            "source_path": "/app/sandbox/directory",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)

        self.assertIn("Error: Path is not a file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_move_file_destination_exists(self, mock_isfile, mock_exists):
        """Test error when destination file already exists."""
        # Mock existence checks: source exists, dest file exists
        mock_exists.side_effect = [True, True]
        mock_isfile.return_value = True

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)

        self.assertIn("Error: Destination file already exists", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    def test_move_file_destination_not_dir(self, mock_isdir, mock_isfile, mock_exists):
        """Test error when destination exists but is not a directory."""
        # Mock existence checks: source exists, dest file doesn't exist, dest dir exists but not a dir
        mock_exists.side_effect = [True, False, True]
        mock_isfile.return_value = True
        mock_isdir.return_value = False

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/somefile.txt",
        }
        result = move_file(params)

        self.assertIn("Error: Destination path exists but is not a directory", result)

    def test_move_file_missing_source_path(self):
        """Test error when source_path is missing."""
        params = {"destination_dir": "/app/sandbox/newdir"}
        result = move_file(params)
        self.assertEqual(result, "Error: source_path parameter is required")

    def test_move_file_missing_destination_dir(self):
        """Test error when destination_dir is missing."""
        params = {"source_path": "/app/sandbox/file.txt"}
        result = move_file(params)
        self.assertEqual(result, "Error: destination_dir parameter is required")

    def test_move_file_invalid_types(self):
        """Test type validation for parameters."""
        # Invalid source_path type
        params = {
            "source_path": 123,
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)
        self.assertEqual(result, "Error: source_path must be a string")

        # Invalid destination_dir type
        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": 456,
        }
        result = move_file(params)
        self.assertEqual(result, "Error: destination_dir must be a string")

        # Invalid new_name type
        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
            "new_name": 789,
        }
        result = move_file(params)
        self.assertEqual(result, "Error: new_name must be a string")

    def test_move_file_outside_sandbox(self):
        """Test security checks for paths outside sandbox."""
        # Source outside sandbox
        params = {
            "source_path": "/etc/passwd",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("Source file must be within", result)

        # Destination outside sandbox
        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/etc",
        }
        result = move_file(params)
        self.assertIn("Error: Access denied", result)
        self.assertIn("Destination must be within", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("shutil.move")
    def test_move_file_permission_error(
        self, mock_move, mock_isdir, mock_isfile, mock_exists
    ):
        """Test handling of permission errors."""
        mock_exists.side_effect = [True, False, True]
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        mock_move.side_effect = PermissionError("Access denied")

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)
        self.assertIn("Error: Permission denied", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("shutil.move")
    def test_move_file_os_error(self, mock_move, mock_isdir, mock_isfile, mock_exists):
        """Test handling of OS errors."""
        mock_exists.side_effect = [True, False, True]
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        mock_move.side_effect = OSError("Cross-device link")

        params = {
            "source_path": "/app/sandbox/file.txt",
            "destination_dir": "/app/sandbox/newdir",
        }
        result = move_file(params)
        self.assertIn("Error: Failed to move file", result)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("shutil.move")
    def test_move_file_nested_paths(
        self, mock_move, mock_makedirs, mock_isdir, mock_isfile, mock_exists
    ):
        """Test moving file with nested directory paths."""
        # Mock existence checks
        mock_exists.side_effect = [True, False, False]
        mock_isfile.return_value = True

        params = {
            "source_path": "/app/sandbox/dir1/subdir/file.txt",
            "destination_dir": "/app/sandbox/dir2/deep/nested",
            "new_name": "moved.txt",
        }
        result = move_file(params)

        self.assertIn("Success", result)
        self.assertIn("dir1/subdir/file.txt", result)
        self.assertIn("dir2/deep/nested/moved.txt", result)
        mock_makedirs.assert_called_once()
        mock_move.assert_called_once()


if __name__ == "__main__":
    unittest.main()
