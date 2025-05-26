"""
Unit test for ExecRspecTestFunction
"""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.function.exec_rspec_test import ExecRspecTestFunction
from src.agent.schema.exec_rspec_test_input import ExecRspecTestInput


class TestExecRspecTestFunction(unittest.TestCase):
    """Test class for ExecRspecTestFunction"""

    @patch("src.agent.function.exec_rspec_test.subprocess.run")
    def test_execute_success(self, mock_run):
        """Test for execute method when it succeeds"""
        # Set up mock
        mock_result = MagicMock()
        mock_result.stdout = "Test success message"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Test execution
        file_path = "spec/test_spec.rb"
        result = ExecRspecTestFunction.execute(file_path)

        # Verification
        mock_run.assert_called_once_with(
            f"bundle exec rspec '{file_path}'",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result["stdout"], "Test success message")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["exit_status"], "0")

    @patch("src.agent.function.exec_rspec_test.subprocess.run")
    def test_execute_error(self, mock_run):
        """Test for execute method when it raises an error"""
        # Set up mock
        from subprocess import CalledProcessError

        mock_error = CalledProcessError(1, "bundle exec rspec 'spec/test_spec.rb'")
        mock_error.stdout = "Error output"
        mock_error.stderr = "Stack trace"
        mock_run.side_effect = mock_error

        # Test execution
        file_path = "spec/test_spec.rb"
        result = ExecRspecTestFunction.execute(file_path)

        # Verification
        mock_run.assert_called_once_with(
            f"bundle exec rspec '{file_path}'",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result["stdout"], "Error output")
        self.assertEqual(result["stderr"], "stack trace")
        self.assertEqual(result["exit_status"], "1")

    @patch("src.agent.function.exec_rspec_test.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Set up mock
        mock_from_function.return_value = "mock_tool"

        # Test execution
        with patch.object(
            ExecRspecTestFunction,
            "function_name",
            return_value="exec_rspec_test_function",
        ):
            result = ExecRspecTestFunction.to_tool()

        # Verification
        mock_from_function.assert_called_once_with(
            name="exec_rspec_test_function",
            description="Execute RSpec tests on the specified file or directory.",
            func=ExecRspecTestFunction.execute,
            args_schema=ExecRspecTestInput,
        )
        self.assertEqual(result, "mock_tool")


if __name__ == "__main__":
    unittest.main()
