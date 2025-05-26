from pydantic import Field

from src.application.schema.base import BaseInput


class OverwriteFileInput(BaseInput):
    filepath: str = Field(..., description="Path to the target file to overwrite")
    new_text: str = Field(..., description="New content to write")
