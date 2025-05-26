"""
Unit test for GoogleSearchFunction
"""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.function.google_search import GoogleSearchFunction
from src.agent.schema.google_search_input import GoogleSearchInput
from src.application.client.google_search_client import GoogleSearchClient


class TestGoogleSearchFunction(unittest.TestCase):
    """Test class for GoogleSearchFunction"""

    @patch("src.agent.function.google_search.GoogleSearchFunction.search_client")
    def test_execute(self, mock_search_client):
        """Test for execute method"""
        # Set up mock
        mock_item1 = {
            "title": "Test result1",
            "formatted_url": "https://example.com/1",
            "html_snippet": "Test content1",
        }

        mock_item2 = {
            "title": "Test result2",
            "formatted_url": "https://example.com/2",
            "html_snippet": "Test content2",
        }

        mock_result = {"items": [mock_item1, mock_item2]}

        mock_client = MagicMock(spec=GoogleSearchClient)
        mock_client.search.return_value = mock_result
        mock_search_client.return_value = mock_client

        # Test execution
        search_word = "Test search word"
        result = GoogleSearchFunction.execute(search_word)

        # Verification
        mock_client.search.assert_called_once_with(search_word, gl="jp")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "テスト結果1")
        self.assertEqual(result[0]["url"], "https://example.com/1")
        self.assertEqual(result[0]["snippet"], "テストの内容1")
        self.assertEqual(result[1]["title"], "テスト結果2")
        self.assertEqual(result[1]["url"], "https://example.com/2")
        self.assertEqual(result[1]["snippet"], "テストの内容2")

    @patch("src.agent.function.google_search.GoogleSearchClient")
    def test_search_client(self, mock_client_class):
        """Test for search_client method"""
        # Reset class variable
        GoogleSearchFunction._search_client = None

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # First call
        client1 = GoogleSearchFunction.search_client()
        mock_client_class.assert_called_once()

        # Second call (new instance is not created)
        client2 = GoogleSearchFunction.search_client()
        mock_client_class.assert_called_once()  # Number of calls does not change

        # Check that the same instance is returned
        self.assertEqual(client1, client2)

    @patch("src.agent.function.google_search.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        mock_tool = MagicMock()
        mock_from_function.return_value = mock_tool

        # Mock
        with patch.object(
            GoogleSearchFunction, "function_name", return_value="google_search_function"
        ):
            tool = GoogleSearchFunction.to_tool()

        mock_from_function.assert_called_once_with(
            name="google_search_function",
            description="Execute Google search with the specified keyword and return the result.",
            func=GoogleSearchFunction.execute,
            args_schema=GoogleSearchInput,
        )
        self.assertEqual(tool, mock_tool)


if __name__ == "__main__":
    unittest.main()
