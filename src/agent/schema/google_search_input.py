from pydantic import Field

from src.application.schema.base import BaseInput


class GoogleSearchInput(BaseInput):
    """Input for searching Google"""

    search_word: str = Field(..., description="Keyword to search")
