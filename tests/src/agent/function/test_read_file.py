import unittest
from unittest.mock import mock_open, patch

from src.agent.function.read_file import ReadFileFunction
from src.agent.schema.read_file_input import ReadFileInput


class TestReadFileFunction(unittest.TestCase):
    """
    Test cases for ReadFileFunction

    Test the following cases:
    - Normal case when file exists
    - Error handling when file does not exist
    - Check that to_tool function works correctly
    """

    def test_execute_file_exists(self):
        """Test for normal case when file exists"""
        file_content = "Test content"
        filepath = "test_file.txt"

        # Mock when file is opened
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=file_content)),
        ):
            result = ReadFileFunction.execute(filepath)

            self.assertEqual(result["filepath"], filepath)
            self.assertEqual(result["file_contents"], file_content)

    def test_execute_file_not_exists(self):
        """Test for error handling when file does not exist"""
        filepath = "non_existent_file.txt"

        # Mock that file does not exist
        with patch("os.path.exists", return_value=False):
            result = ReadFileFunction.execute(filepath)

            self.assertEqual(result["filepath"], filepath)
            self.assertEqual(result["error"], "File not found.")

    def test_to_tool(self):
        """Check that to_tool function returns StructuredTool correctly"""
        tool = ReadFileFunction.to_tool()

        self.assertEqual(tool.name, "read_file_function")
        self.assertEqual(
            tool.description, "Read the specified file and return the content."
        )
        self.assertEqual(tool.args_schema, ReadFileInput)


if __name__ == "__main__":
    unittest.main()
