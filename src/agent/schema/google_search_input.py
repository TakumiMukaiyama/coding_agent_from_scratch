from pydantic import Field

from src.application.schema.base import BaseInput


class GoogleSearchInput(BaseInput):
    search_word: str = Field(..., description="検索するキーワード")
