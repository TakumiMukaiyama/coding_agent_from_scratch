"""
ECSタスク関連のスキーマ定義

このモジュールはECS関連の操作に必要なデータモデルをPydanticを使って定義します。
"""

from pydantic import BaseModel, Field


class TaskExecutionResult(BaseModel):
    """
    ECSタスク実行結果を保持するPydanticモデル

    Attributes:
        task_arn (str): タスクARN
        cluster_name (str): クラスター名
    """

    task_arn: str = Field(..., description="ECSタスクのARN")
    cluster_name: str = Field(..., description="ECSクラスターの名前")
