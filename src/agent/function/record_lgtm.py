import threading
from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.record_lgtm_input import RecordLgtmInput
from src.application.function.base import BaseFunction


class RecordLgtmFunction(BaseFunction):
    """
    LGTM（Looks Good To Me）を記録するためのツール
    """

    # スレッドローカルストレージで状態を管理（スレッドセーフ）
    _thread_local = threading.local()

    def __init__(self):
        """初期化時にLGTM状態をリセットする"""
        self.reset_lgtm()

    @classmethod
    def lgtm(cls) -> bool:
        """現在のLGTM状態を返す"""
        return getattr(cls._thread_local, "lgtm_status", False)

    @classmethod
    def reset_lgtm(cls) -> None:
        """LGTM状態をリセットする"""
        cls._thread_local.lgtm_status = False

    @staticmethod
    def execute(**kwargs) -> Dict[str, str]:
        """LGTM状態をTrueに設定する"""
        from src.infrastructure.utils.logger import get_logger

        logger = get_logger(__name__)

        RecordLgtmFunction._thread_local.lgtm_status = True
        logger.info("RecordLgtmFunction.execute() が呼び出されました - LGTM状態をTrueに設定")
        return {"result": "LGTMを記録しました"}

    @classmethod
    def to_tool(cls: Type["RecordLgtmFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="現在の作業をLGTM（Looks Good To Me）と記録します。",
            func=cls.execute,
            args_schema=RecordLgtmInput,
        )
