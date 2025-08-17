"""Tests for list_files tool."""

import unittest
from unittest.mock import MagicMock, patch

from src.tools.list_files import TOOL_METADATA, list_files


class TestListFiles(unittest.TestCase):
    """Test cases for list_files tool."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock file structure
        self.mock_files = [
            "/app/sandbox/file1.txt",
            "/app/sandbox/subdir/file2.py",
            "/app/sandbox/subdir/nested/file3.md",
            "/app/sandbox/.hidden.txt",  # Hidden file
            "/app/sandbox/.hidden_dir/file4.txt",  # File in hidden directory
        ]

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_success_default_directory(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test successful file listing with default directory."""
        # Setup mocks
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox" if x == "/app/sandbox" else x
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True

        # Mock os.walk to return our test file structure
        mock_walk.return_value = [
            ("/app/sandbox", ["subdir"], ["file1.txt"]),
            ("/app/sandbox/subdir", ["nested"], ["file2.py"]),
            ("/app/sandbox/subdir/nested", [], ["file3.md"]),
        ]

        params = {}
        result = list_files(params)

        self.assertIn("Found 3 files", result)
        self.assertIn("/app/sandbox/file1.txt", result)
        self.assertIn("/app/sandbox/subdir/file2.py", result)
        self.assertIn("/app/sandbox/subdir/nested/file3.md", result)

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_with_custom_directory(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test file listing with custom directory path."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox/subdir"
            if x == "/app/sandbox/subdir"
            else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_walk.return_value = [
            ("/app/sandbox/subdir", ["nested"], ["file2.py"]),
            ("/app/sandbox/subdir/nested", [], ["file3.md"]),
        ]

        params = {"directory_path": "/app/sandbox/subdir"}
        result = list_files(params)

        self.assertIn("Found 2 files", result)
        self.assertIn("/app/sandbox/subdir/file2.py", result)
        self.assertIn("/app/sandbox/subdir/nested/file3.md", result)

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_show_hidden(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test file listing with hidden files shown."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox" if x == "/app/sandbox" else x
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_walk.return_value = [
            ("/app/sandbox", ["subdir", ".hidden_dir"], ["file1.txt", ".hidden.txt"]),
            ("/app/sandbox/subdir", [], ["file2.py"]),
            ("/app/sandbox/.hidden_dir", [], ["file4.txt"]),
        ]

        params = {"show_hidden": True}
        result = list_files(params)

        self.assertIn("Found 4 files", result)
        self.assertIn("/app/sandbox/file1.txt", result)
        self.assertIn("/app/sandbox/.hidden.txt", result)
        self.assertIn("/app/sandbox/subdir/file2.py", result)
        self.assertIn("/app/sandbox/.hidden_dir/file4.txt", result)

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_hide_hidden(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test file listing with hidden files hidden (default behavior)."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox" if x == "/app/sandbox" else x
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True

        # Mock os.walk with filtering applied (simulating the real behavior)
        walk_mock = MagicMock()
        walk_mock.__iter__ = MagicMock(
            return_value=iter(
                [
                    (
                        "/app/sandbox",
                        ["subdir"],
                        ["file1.txt"],
                    ),  # .hidden.txt filtered out, .hidden_dir filtered from dirs
                    ("/app/sandbox/subdir", [], ["file2.py"]),
                ]
            )
        )
        mock_walk.return_value = walk_mock

        params = {"show_hidden": False}
        result = list_files(params)

        self.assertIn("Found 2 files", result)
        self.assertIn("/app/sandbox/file1.txt", result)
        self.assertIn("/app/sandbox/subdir/file2.py", result)
        self.assertNotIn(".hidden", result)

    def test_list_files_invalid_directory_type(self):
        """Test with invalid directory path type."""
        params = {"directory_path": 123}
        result = list_files(params)
        self.assertEqual(result, "Error: directory_path must be a string")

    def test_list_files_invalid_show_hidden_type(self):
        """Test with invalid show_hidden type."""
        params = {"show_hidden": "true"}
        result = list_files(params)
        self.assertEqual(result, "Error: show_hidden must be a boolean")

    @patch("src.tools.list_files.os.path.abspath")
    def test_list_files_outside_sandbox(self, mock_abspath):
        """Test access denied for directories outside sandbox."""
        mock_abspath.side_effect = lambda x: "/etc" if x == "/etc" else "/app/sandbox"

        params = {"directory_path": "/etc"}
        result = list_files(params)
        self.assertIn("Error: Access denied", result)

    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    def test_list_files_directory_not_found(self, mock_exists, mock_abspath):
        """Test directory not found error."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox/nonexistent"
            if x == "/app/sandbox/nonexistent"
            else "/app/sandbox"
        )
        mock_exists.return_value = False

        params = {"directory_path": "/app/sandbox/nonexistent"}
        result = list_files(params)
        self.assertIn("Error: Directory not found", result)

    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_path_is_file(self, mock_isdir, mock_exists, mock_abspath):
        """Test error when path is a file, not directory."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox/file.txt"
            if x == "/app/sandbox/file.txt"
            else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isdir.return_value = False

        params = {"directory_path": "/app/sandbox/file.txt"}
        result = list_files(params)
        self.assertIn("Error: Path is not a directory", result)

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_empty_directory(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test listing empty directory."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox/empty"
            if x == "/app/sandbox/empty"
            else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_walk.return_value = [("/app/sandbox/empty", [], [])]

        params = {"directory_path": "/app/sandbox/empty"}
        result = list_files(params)
        self.assertIn("No files found", result)

    @patch("src.tools.list_files.os.walk")
    @patch("src.tools.list_files.os.path.abspath")
    @patch("src.tools.list_files.os.path.exists")
    @patch("src.tools.list_files.os.path.isdir")
    def test_list_files_permission_error(
        self, mock_isdir, mock_exists, mock_abspath, mock_walk
    ):
        """Test permission error handling."""
        mock_abspath.side_effect = (
            lambda x: "/app/sandbox/protected"
            if x == "/app/sandbox/protected"
            else "/app/sandbox"
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_walk.side_effect = PermissionError("Permission denied")

        params = {"directory_path": "/app/sandbox/protected"}
        result = list_files(params)
        self.assertIn("Error: Permission denied", result)

    def test_tool_metadata(self):
        """Test tool metadata is correctly defined."""
        self.assertEqual(TOOL_METADATA["name"], "list_files")
        self.assertEqual(TOOL_METADATA["handler"], list_files)
        self.assertIn("description", TOOL_METADATA)
        self.assertIn("input_schema", TOOL_METADATA)

        # Test schema structure
        schema = TOOL_METADATA["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("directory_path", schema["properties"])
        self.assertIn("show_hidden", schema["properties"])
        self.assertEqual(schema["required"], [])

    def test_tool_metadata_schema(self):
        """Test that tool metadata schema is valid."""
        schema = TOOL_METADATA["input_schema"]

        # Verify directory_path property
        dir_path_prop = schema["properties"]["directory_path"]
        self.assertEqual(dir_path_prop["type"], "string")
        self.assertIn("description", dir_path_prop)

        # Verify show_hidden property
        show_hidden_prop = schema["properties"]["show_hidden"]
        self.assertEqual(show_hidden_prop["type"], "boolean")
        self.assertIn("description", show_hidden_prop)
