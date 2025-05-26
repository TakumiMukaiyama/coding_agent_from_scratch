from pydantic import Field

from src.application.schema.base import BaseInput


class OpenUrlInput(BaseInput):
    url: str = Field(..., description="取得するWebページのURL")
    what_i_want_to_know: str = Field(..., description="このページから知りたいこと")
