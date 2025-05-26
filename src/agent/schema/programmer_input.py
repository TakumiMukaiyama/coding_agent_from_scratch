from pydantic import Field

from src.application.schema.base import BaseInput


# 入力スキーマの定義
class ProgrammerInput(BaseInput):
    """プログラマーエージェントへの入力スキーマ"""

    instruction: str = Field(description="ユーザーからの指示")


