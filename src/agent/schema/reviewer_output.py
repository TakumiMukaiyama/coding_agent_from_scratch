from typing import List
from pydantic import Field

from src.application.schema.base import BaseOutput


class ReviewerOutput(BaseOutput):
    """
    コードレビュー後の出力データ
    """

    summary: str = Field(..., description="レビューまとめコメント")
    suggestions: List[str] = Field(
        default_factory=list, description="発見された問題点や改善提案リスト"
    )
    lgtm: bool = Field(..., description="問題なければTrue（Looks Good To Me）")
