from pydantic import Field
from src.application.schema.base import BaseInput


class OverwriteFileInput(BaseInput):
    filepath: str = Field(..., description="上書きする対象ファイルのパス")
    new_text: str = Field(..., description="新しく書き込む内容")
