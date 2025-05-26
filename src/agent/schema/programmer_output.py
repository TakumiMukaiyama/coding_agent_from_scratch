from pydantic import Field

from src.application.schema.base import BaseOutput


# 出力スキーマの定義
class ProgrammerOutput(BaseOutput):
    """プログラマーエージェントからの出力スキーマ"""

    result: str = Field(description="エージェントからの応答結果")
