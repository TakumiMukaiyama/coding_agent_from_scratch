from src.application.schema.base import BaseInput
from pydantic import Field


class GeneratePRParamsInput(BaseInput):
    """プルリクエストパラメータ生成用の入力データ"""

    instruction: str = Field(..., description="プログラマーへの指示内容")
    programmer_output: str = Field(..., description="プログラマーの出力内容")
    diff: str = Field(default="", description="コードの差分（オプション）") 