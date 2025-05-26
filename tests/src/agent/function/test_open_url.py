import unittest
from unittest.mock import MagicMock, patch

import requests

from src.agent.function.open_url import OpenUrlFunction


class TestOpenUrlFunction(unittest.TestCase):
    """Test class for OpenUrlFunction"""

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_normal_case(self, mock_get):
        """Test for normal case with short content"""
        # Set up mock
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>Test page</title></head><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test execution
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="Test information"
        )

        # Verification
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "Test page")
        self.assertIn("Test content", result["page_content"])
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("src.agent.function.open_url.requests.get")
    @patch("src.agent.function.open_url.AzureOpenAIClient")
    def test_execute_long_content_case(self, mock_azure_client, mock_get):
        """Test for long content case"""
        # Set up mock - generate long content
        mock_response = MagicMock()
        mock_response.text = (
            "<html><head><title>Long page</title></head><body>"
            + "Test" * 10000
            + "</body></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock Azure OpenAI client
        mock_chat = MagicMock()
        mock_chat.invoke.return_value = MagicMock(content="Summarized content")
        mock_azure_client.return_value.initialize_chat.return_value = mock_chat

        # Test execution
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="Long information"
        )

        # Verification
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "Long page")
        self.assertIn("Summarized content", result["page_content"])
        mock_get.assert_called_once_with("https://example.com", timeout=10)
        self.assertTrue(mock_chat.invoke.called)

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_http_error(self, mock_get):
        """Test for HTTP error case"""
        # Set up mock - generate HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # Verify that an error occurs
        with self.assertRaises(requests.HTTPError):
            OpenUrlFunction.execute(
                url="https://example.com/not-found",
                what_i_want_to_know="Non-existent information",
            )

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_no_title(self, mock_get):
        """Test for HTML with no title"""
        # Set up mock - HTML with no title
        mock_response = MagicMock()
        mock_response.text = "<html><body>No title content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test execution
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="Information"
        )

        # Verification
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "")
        self.assertIn("No title content", result["page_content"])

    @patch("src.agent.function.open_url.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Set up mock
        mock_tool = MagicMock()
        mock_tool.name = "open_url_function"
        mock_tool.description = "Open the specified URL, get the page content, and summarize it."
        mock_from_function.return_value = mock_tool

        # Test execution
        tool = OpenUrlFunction.to_tool()

        # Verification
        self.assertEqual(tool.name, "open_url_function")
        self.assertEqual(
            tool.description, "Open the specified URL, get the page content, and summarize it."
        )

        # Verify that from_function is called with the correct parameters
        mock_from_function.assert_called_once()
        # Verify that the name is passed correctly (bypass the behavior of BaseFunction.function_name with mock)
        args, kwargs = mock_from_function.call_args
        self.assertEqual(kwargs["func"], OpenUrlFunction.execute)
        self.assertEqual(
            kwargs["description"],
            "Open the specified URL, get the page content, and summarize it.",
        )


if __name__ == "__main__":
    unittest.main()
    