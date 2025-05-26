from typing import Any

from googleapiclient.discovery import build

from src.infrastructure.config.google_search_settings import google_search_settings


class GoogleSearchClient:
    def __init__(self) -> None:
        self.api_key = google_search_settings.GOOGLE_API_KEY
        self.cx = google_search_settings.CUSTOM_SEARCH_ENGINE_ID
        self._service = None

    def get_service(self) -> Any:
        if self._service is None:
            self._service = build(
                "customsearch",
                "v1",
                developerKey=self.api_key,
            )
        return self._service

    def search(self, query: str, num: int = 10, start: int = 1) -> dict:
        """
        Execute Google search with the specified query and return search results.

        Args:
            query (str): Search term
            num (int, optional): Number of results to retrieve (default 10)
            start (int, optional): Starting index (default 1)

        Returns:
            dict: API response (JSON format)
        """
        service = self.get_service()
        response = (
            service.cse()
            .list(
                q=query,
                cx=self.cx,
                lr="lang_ja",
                num=num,
                start=start,
            )
            .execute()
        )
        return response
