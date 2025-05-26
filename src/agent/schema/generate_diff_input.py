from src.application.schema.base import BaseInput
from pydantic import Field


class GenerateDiffInput(BaseInput):
    """差分生成用の入力データ."""

    base_branch: str = Field(
        default="main", description="比較元のブランチ名（デフォルトはmain）"
    )
    target_branch: str | None = Field(
        default=None, description="比較先のブランチ名（デフォルトは現在のブランチ）"
    )
    file_path: str | None = Field(
        default=None, description="特定のファイルパス（指定しない場合は全ファイル）"
    )
