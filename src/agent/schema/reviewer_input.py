from typing import Optional
from pydantic import Field

from src.application.schema.base import BaseInput


class ReviewerInput(BaseInput):
    """
    コードレビュー用の入力データ
    """

    diff: str = Field(..., description="レビュー対象のコード差分（Unified Diff形式）")
    programmer_comment: Optional[str] = Field(
        None, description="プログラマーからの補足説明（任意）"
    )
