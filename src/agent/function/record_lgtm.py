from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.record_lgtm_input import RecordLgtmInput
from src.application.function.base import BaseFunction


class RecordLgtmFunction(BaseFunction):
    """
    LGTM（Looks Good To Me）を記録するためのツール
    """

    # クラス変数として状態を管理
    _lgtm_status = False

    def __init__(self):
        """初期化時にLGTM状態をリセットする"""
        self.reset_lgtm()

    @classmethod
    def lgtm(cls) -> bool:
        """現在のLGTM状態を返す"""
        return cls._lgtm_status

    @classmethod
    def reset_lgtm(cls) -> None:
        """LGTM状態をリセットする"""
        cls._lgtm_status = False

    @staticmethod
    def execute(**kwargs) -> Dict[str, str]:
        """LGTM状態をTrueに設定する"""
        RecordLgtmFunction._lgtm_status = True
        return {"result": "LGTMを記録しました"}

    @classmethod
    def to_tool(cls: Type["RecordLgtmFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="現在の作業をLGTM（Looks Good To Me）と記録します。",
            func=cls.execute,
            args_schema=RecordLgtmInput,
        )
