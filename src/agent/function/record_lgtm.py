import threading
from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.record_lgtm_input import RecordLgtmInput
from src.application.function.base import BaseFunction


class RecordLgtmFunction(BaseFunction):
    """
    Tool for recording LGTM (Looks Good To Me)
    """

    # Manage state with thread-local storage (thread-safe)
    _thread_local = threading.local()

    def __init__(self):
        """Reset LGTM status during initialization"""
        self.reset_lgtm()

    @classmethod
    def lgtm(cls) -> bool:
        """Return current LGTM status"""
        return getattr(cls._thread_local, "lgtm_status", False)

    @classmethod
    def reset_lgtm(cls) -> None:
        """Reset LGTM status"""
        cls._thread_local.lgtm_status = False

    @staticmethod
    def execute(**kwargs) -> Dict[str, str]:
        """Set LGTM status to True"""
        from src.infrastructure.utils.logger import get_logger

        logger = get_logger(__name__)

        RecordLgtmFunction._thread_local.lgtm_status = True
        logger.info("RecordLgtmFunction.execute() was called - Set LGTM status to True")
        return {"result": "LGTM recorded"}

    @classmethod
    def to_tool(cls: Type["RecordLgtmFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Record the current work as LGTM (Looks Good To Me).",
            func=cls.execute,
            args_schema=RecordLgtmInput,
        )
