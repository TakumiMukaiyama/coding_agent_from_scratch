from pydantic import Field

from src.application.schema.base import BaseInput


class ReadFileInput(BaseInput):
    """Input for reading a file"""

    filepath: str = Field(..., description="Path to the target file to read")
