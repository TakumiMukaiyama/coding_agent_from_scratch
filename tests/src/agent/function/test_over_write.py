"""
Unit tests for OverwriteFileFunction
"""

import unittest
from unittest.mock import mock_open, patch

from src.agent.function.over_write_file import OverwriteFileFunction
from src.agent.schema.over_write_input import OverwriteFileInput


class TestOverwriteFileFunction(unittest.TestCase):
    """Test class for OverwriteFileFunction"""

    @patch("src.agent.function.over_write_file.open", new_callable=mock_open)
    def test_execute(self, mock_file):
        """Test for overwriting a file"""
        # Execute test
        filepath = "test_dir/test_file.txt"
        new_text = "New test content"
        result = OverwriteFileFunction.execute(filepath=filepath, new_text=new_text)

        # Verify
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(new_text)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.over_write_file.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Mock setup
        mock_from_function.return_value = "mock_tool"

        # Execute test
        with patch.object(OverwriteFileFunction, "function_name", return_value="overwrite_file"):
            result = OverwriteFileFunction.to_tool()

        # Verify
        mock_from_function.assert_called_once_with(
            name="overwrite_file",
            description="Overwrites the specified file with new content.",
            func=OverwriteFileFunction.execute,
            args_schema=OverwriteFileInput,
        )
        self.assertEqual(result, "mock_tool")


def test_execute_with_real_filesystem(tmp_path):
    """Test using actual filesystem"""
    # Set test file path
    test_file = tmp_path / "test_file.txt"

    # Create file with initial content
    initial_content = "Initial content"
    test_file.write_text(initial_content, encoding="utf-8")

    # New content for overwriting
    new_content = "New content"

    # Execute function
    result = OverwriteFileFunction.execute(filepath=str(test_file), new_text=new_content)

    # Verify
    assert result == {"result": "success"}
    assert test_file.exists()  # Check if file exists
    assert test_file.read_text(encoding="utf-8") == new_content  # Check if content was overwritten
    assert test_file.read_text(encoding="utf-8") != initial_content  # Check if it's not the initial content


if __name__ == "__main__":
    unittest.main()
