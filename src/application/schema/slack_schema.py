"""
Slack関連のスキーマ定義

このモジュールはSlack関連の操作に必要なデータモデルをPydanticを使って定義します。
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class SlackSessions(BaseModel):
    """
    Slackセッション情報を保持するPydanticモデル

    Attributes:
        session_id (str): セッションID（UUID）- DynamoDBのパーティションキー（session_id）
        channel_id (str): SlackチャンネルID - GSIのパーティションキー
        thread_ts (str): Slackスレッドタイムスタンプ - GSIのソートキー
        pr_id (str): GitHub PR ID - GSIのパーティションキー
        github_id (str): GitHub ID
        user_id (str): ユーザーID
        user_email (str): ユーザーメールアドレス
        user_real_name (str): ユーザー実名
        status (str): 処理ステータス
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
        expires_at (int): TTLの有効期限（エポック秒）
    """

    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="セッションID（パーティションキー）",
    )
    channel_id: str = Field(..., description="SlackチャンネルID")
    thread_ts: str = Field(..., description="Slackスレッドタイムスタンプ")
    pr_id: Optional[str] = Field(None, description="GitHub PR ID")
    github_id: Optional[str] = Field(None, description="GitHub ID")
    user_id: Optional[str] = Field(None, description="ユーザーID")
    user_email: Optional[str] = Field(None, description="ユーザーメールアドレス")
    user_real_name: Optional[str] = Field(None, description="ユーザー実名")
    status: str = Field(default="RUNNING", description="処理ステータス")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")
    expires_at: int = Field(
        default_factory=lambda: int((datetime.now() + timedelta(days=30)).timestamp()),
        description="TTLの有効期限（エポック秒）",
    )

    def model_dump(self) -> Dict[str, Any]:
        """モデルをDynamoDB用の辞書に変換する

        Returns:
            Dict[str, Any]: DynamoDB用の辞書
        """
        data = super().model_dump()

        # datetimeオブジェクトを文字列に変換
        if "created_at" in data and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()

        if "updated_at" in data and isinstance(data["updated_at"], datetime):
            data["updated_at"] = data["updated_at"].isoformat()

        # pr_idがNULLの場合にデフォルト値を設定（GSIのキーとして必要）
        if data.get("pr_id") is None:
            data["pr_id"] = "NONE"  # DynamoDBのGSIキーとしてNULLを避ける

        return data

    @classmethod
    def get_key(cls, session_id: str) -> Dict[str, str]:
        """指定されたIDに対応するDynamoDBのキー辞書を取得する

        Args:
            session_id (str): セッションID

        Returns:
            Dict[str, str]: DynamoDBのキー辞書
        """
        return {"session_id": session_id}
