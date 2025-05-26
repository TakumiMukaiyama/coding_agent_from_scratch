from pydantic import Field
from src.application.schema.base import BaseInput


class MakeNewFileInput(BaseInput):
    """Input for creating a new file"""

    filepath: str = Field(..., description="Path of the file to create")
    file_contents: str = Field(..., description="Contents to write to the file")
