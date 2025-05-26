from typing import Any

from src.agent.schema.reviewer_input import ReviewerInput
from src.application.function.base import BaseFunction
from langchain_core.tools import StructuredTool


class ReviewCodeFunction(BaseFunction):
    """コードレビューを行うためのツール."""

    @staticmethod
    def execute(diff: str, programmer_comment: str | None = None) -> dict[str, Any]:
        """LLMのFunctionCallingでレビュー結果を生成する前提.

        ここではスタブ応答を返すだけで例外を起こさない.
        """
        return {
            "message": "Handled by LLM FunctionCalling. No real processing done here."
        }

    @classmethod
    def to_tool(cls: type["ReviewCodeFunction"]) -> StructuredTool:
        """ツールを作成する."""
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="プルリクエストのコード差分をレビューし、問題点や改善点をまとめ、LGTM可否を判断します。",
            func=cls.execute,
            args_schema=ReviewerInput,
        )
