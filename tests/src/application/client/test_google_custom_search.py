"""
Unit test module for GoogleSearchClient class

Test for GoogleSearchClient class that uses Google Custom Search API
"""

import unittest
from unittest.mock import MagicMock, patch

from src.application.client.google_search_client import GoogleSearchClient


class TestGoogleSearchClient(unittest.TestCase):
    """Test case for GoogleSearchClient class"""

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def setUp(self, mock_settings, mock_build):
        """Setup before tests"""
        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # Mock build
        self.mock_service = MagicMock()
        mock_build.return_value = self.mock_service

        # Create test instance
        self.client = GoogleSearchClient()

        # Check that build is not called (not called during initialization)
        mock_build.assert_not_called()

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_get_service(self, mock_settings, mock_build):
        """Test for get_service method"""
        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # Mock build
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create test instance
        client = GoogleSearchClient()

        # Call get_service
        service = client.get_service()

        # Check that build is called
        mock_build.assert_called_once_with(
            "customsearch",
            "v1",
            developerKey="test_api_key",
        )

        # Check that the same service is returned
        self.assertEqual(service, mock_service)

        # Check that build is not called the second time
        service = client.get_service()
        mock_build.assert_called_once()  # Check that the number of calls is the same

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_search(self, mock_settings, mock_build):
        """Test for search method"""
        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # Mock build
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Set return value
        mock_execute.return_value = {"items": [{"title": "Test result"}]}
        mock_list.execute.return_value = mock_execute.return_value
        mock_cse.list.return_value = mock_list
        mock_service = MagicMock()
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # Create test instance
        client = GoogleSearchClient()

        # Execute search
        result = client.search("Test search", num=5, start=2)

        # Check that build is called
        mock_build.assert_called_once_with(
            "customsearch",
            "v1",
            developerKey="test_api_key",
        )

        # Check that list method is called
        mock_cse.list.assert_called_once_with(
            q="Test search",
            cx="test_cx_id",
            lr="lang_ja",
            num=5,
            start=2,
        )

        # Check that execute method is called
        mock_list.execute.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, {"items": [{"title": "Test result"}]})

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_search_with_default_params(self, mock_settings, mock_build):
        """Test for search method with default parameters"""
        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # Mock build
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Set return value
        mock_execute.return_value = {"items": [{"title": "Test result"}]}
        mock_list.execute.return_value = mock_execute.return_value
        mock_cse.list.return_value = mock_list
        mock_service = MagicMock()
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # Create test instance
        client = GoogleSearchClient()

        # Execute search with default parameters
        result = client.search("Test search")

        # Check that list method is called
        mock_cse.list.assert_called_once_with(
            q="Test search",
            cx="test_cx_id",
            lr="lang_ja",
            num=10,  # Default value
            start=1,  # Default value
        )

        # Check that the result is correct
        self.assertEqual(result, {"items": [{"title": "Test result"}]})


if __name__ == "__main__":
    unittest.main()
