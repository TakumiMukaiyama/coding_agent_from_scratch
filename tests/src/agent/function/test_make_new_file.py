"""
Unit tests for MakeNewFileFunction
"""

import unittest
from unittest.mock import mock_open, patch

from src.agent.function.make_new_file import MakeNewFileFunction
from src.agent.schema.make_new_file_input import MakeNewFileInput


class TestMakeNewFileFunction(unittest.TestCase):
    """Test class for MakeNewFileFunction"""

    @patch("src.agent.function.make_new_file.os.path.exists")
    @patch("src.agent.function.make_new_file.os.makedirs")
    @patch("src.agent.function.make_new_file.open", new_callable=mock_open)
    def test_execute_with_existing_directory(
        self, mock_file, mock_makedirs, mock_exists
    ):
        """Test creating a file in an existing directory"""
        # Mock setup
        mock_exists.return_value = True

        # Execute test
        filepath = "existing_dir/test_file.txt"
        file_contents = "Test content"
        result = MakeNewFileFunction.execute(
            filepath=filepath, file_contents=file_contents
        )

        # Verification
        mock_exists.assert_called_once_with("existing_dir")
        mock_makedirs.assert_not_called()  # Directory already exists, so not created
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(file_contents)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.make_new_file.os.path.exists")
    @patch("src.agent.function.make_new_file.os.makedirs")
    @patch("src.agent.function.make_new_file.open", new_callable=mock_open)
    def test_execute_with_new_directory(self, mock_file, mock_makedirs, mock_exists):
        """Test creating a file in a new directory"""
        # Mock setup
        mock_exists.return_value = False

        # Execute test
        filepath = "new_dir/test_file.txt"
        file_contents = "Test content"
        result = MakeNewFileFunction.execute(
            filepath=filepath, file_contents=file_contents
        )

        # Verification
        mock_exists.assert_called_once_with("new_dir")
        mock_makedirs.assert_called_once_with("new_dir", exist_ok=True)
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(file_contents)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.make_new_file.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Mock setup
        mock_from_function.return_value = "mock_tool"

        # Execute test
        with patch.object(
            MakeNewFileFunction, "function_name", return_value="make_new_file"
        ):
            result = MakeNewFileFunction.to_tool()

        # Verification
        mock_from_function.assert_called_once_with(
            name="make_new_file",
            description="Creates a new file and writes the specified content to it.",
            func=MakeNewFileFunction.execute,
            args_schema=MakeNewFileInput,
        )
        self.assertEqual(result, "mock_tool")


def test_execute_with_real_filesystem(tmp_path):
    """Test using actual filesystem"""
    # Set up test directory and file paths
    test_dir = tmp_path / "test_dir"
    test_file = test_dir / "test_file.txt"
    file_contents = "Test content for file"

    # Execute function
    result = MakeNewFileFunction.execute(
        filepath=str(test_file), file_contents=file_contents
    )

    # Verification
    assert result == {"result": "success"}
    assert test_dir.exists()  # Check if directory was created
    assert test_file.exists()  # Check if file was created
    assert (
        test_file.read_text(encoding="utf-8") == file_contents
    )  # Check if content is correct


if __name__ == "__main__":
    unittest.main()
