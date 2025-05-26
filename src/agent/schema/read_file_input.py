from pydantic import Field

from src.application.schema.base import BaseInput


class ReadFileInput(BaseInput):
    filepath: str = Field(..., description="読み取る対象ファイルのパス")
