from pydantic import Field

from src.application.schema.base import BaseInput


class GeneratePullRequestParamsInput(BaseInput):
    title: str = Field(..., description="PRのタイトル")
    description: str = Field(..., description="PRの説明文")
    branch_name: str = Field(..., description="PRを作成するブランチ名")
