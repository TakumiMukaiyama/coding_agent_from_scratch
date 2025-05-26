from src.application.schema.base import BaseInput
from pydantic import Field


class GitCommitPushInput(BaseInput):
    """Git変更コミット＆プッシュ用の入力データ"""

    path_to_add: str = Field(default=".", description="addするパス（デフォルトは全ての変更）")
    commit_message: str = Field(default="", description="コミットメッセージ（空の場合は自動生成）")
    remote_name: str = Field(default="origin", description="リモート名")
    branch_name: str = Field(default="", description="プッシュ先のブランチ名（空の場合は現在のブランチ）")
    force_push: bool = Field(default=False, description="強制プッシュするかどうか") 