"""
Unit test for GeneratePullRequestParamsFunction
"""

import unittest
from unittest.mock import patch

from src.agent.function.generate_pull_request_params import (
    GeneratePullRequestParamsFunction,
)
from src.agent.schema.generate_pull_request_params_input import (
    GeneratePullRequestParamsInput,
)


class TestGeneratePullRequestParamsFunction(unittest.TestCase):
    """Test class for GeneratePullRequestParamsFunction"""

    def test_execute(self):
        """Test for execute method"""
        # Create test instance
        function = GeneratePullRequestParamsFunction()

        # Prepare parameters
        title = "Test PR title"
        description = "Test PR description"
        branch_name = "test/branch-name"

        # Test execution
        result = function.execute(
            title=title, description=description, branch_name=branch_name
        )

        # Verification
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(function.title, title)
        self.assertEqual(function.description, description)
        self.assertEqual(function.branch_name, branch_name)

    @patch(
        "src.agent.function.generate_pull_request_params.StructuredTool.from_function"
    )
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Set up mock
        mock_from_function.return_value = "mock_tool"

        # Test execution
        with patch.object(
            GeneratePullRequestParamsFunction,
            "function_name",
            return_value="generate_pull_request_params_function",
        ):
            result = GeneratePullRequestParamsFunction.to_tool()

        # Verification
        mock_from_function.assert_called_once()
        self.assertEqual(
            mock_from_function.call_args[1]["name"],
            "generate_pull_request_params_function",
        )
        self.assertEqual(
            mock_from_function.call_args[1]["description"],
            "Generate title, description, and branch name for Pull Request.",
        )
        # Check that
        self.assertTrue(callable(mock_from_function.call_args[1]["func"]))
        self.assertEqual(
            mock_from_function.call_args[1]["args_schema"],
            GeneratePullRequestParamsInput,
        )
        self.assertEqual(result, "mock_tool")

    def test_wrapper_functionality(self):
        """Test for wrapper function"""
        # Get wrapper function using mock
        with (
            patch(
                "src.agent.function.generate_pull_request_params.StructuredTool.from_function"
            ) as mock_from_function,
            patch.object(
                GeneratePullRequestParamsFunction,
                "function_name",
                return_value="generate_pull_request_params_function",
            ),
        ):
            GeneratePullRequestParamsFunction.to_tool()
            wrapper_func = mock_from_function.call_args[1]["func"]

        # Check that the instance state is updated before and after being passed to wrapper
        result = wrapper_func(
            title="Wrapped title",
            description="Wrapped description",
            branch_name="wrapped/branch-name",
        )

        self.assertEqual(result, {"result": "success"})


if __name__ == "__main__":
    unittest.main()
