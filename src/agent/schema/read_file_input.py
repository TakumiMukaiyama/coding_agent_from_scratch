from pydantic import Field

from src.application.schema.base import BaseInput


class ReadFileInput(BaseInput):
    filepath: str = Field(..., description="Path to the target file to read")
