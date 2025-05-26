from pydantic import Field
from src.application.schema.base import BaseInput


class MakeNewFileInput(BaseInput):
    filepath: str = Field(..., description="作成するファイルのパス")
    file_contents: str = Field(..., description="ファイルに書き込む内容")
