from src.application.schema.base import BaseInput
from pydantic import Field


class CreateBranchInput(BaseInput):
    """ブランチ作成用の入力データ"""

    branch_name: str = Field(..., description="作成するブランチ名")
