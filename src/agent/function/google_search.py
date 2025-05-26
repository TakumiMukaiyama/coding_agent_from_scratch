from typing import List, Dict, Type
from langchain_core.tools import StructuredTool

from src.application.function.base import BaseFunction
from src.application.client.google_search_client import GoogleSearchClient
from src.agent.schema.google_search_input import GoogleSearchInput


class GoogleSearchFunction(BaseFunction):
    """Function to search Google"""

    _search_client: GoogleSearchClient = None

    @classmethod
    def search_client(cls) -> GoogleSearchClient:
        if cls._search_client is None:
            cls._search_client = GoogleSearchClient()
        return cls._search_client

    @staticmethod
    def execute(search_word: str) -> List[Dict[str, str]]:
        search_results = GoogleSearchFunction.search_client().search(
            search_word, gl="jp"
        )
        return [
            {
                "title": item["title"],
                "url": item["formatted_url"],
                "snippet": item["html_snippet"],
            }
            for item in search_results["items"]
        ]

    @classmethod
    def to_tool(cls: Type["GoogleSearchFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Search Google with the specified keyword and return the results.",
            func=cls.execute,
            args_schema=GoogleSearchInput,
        )
