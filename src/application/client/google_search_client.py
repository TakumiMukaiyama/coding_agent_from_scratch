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
        指定したクエリでGoogle検索を実行し、検索結果を返す。

        Args:
            query (str): 検索ワード
            num (int, optional): 取得件数（デフォルト10件）
            start (int, optional): 開始インデックス（デフォルト1）

        Returns:
            dict: APIレスポンス（JSON形式）
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
