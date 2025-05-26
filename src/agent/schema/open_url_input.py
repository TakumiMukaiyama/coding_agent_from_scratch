from pydantic import Field

from src.application.schema.base import BaseInput


class OpenUrlInput(BaseInput):
    """Input for opening a web page"""

    url: str = Field(..., description="URL of the web page to retrieve")
    what_i_want_to_know: str = Field(..., description="What I want to know from this page")
