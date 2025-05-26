"""
ECSクライアントモジュール

このモジュールはECSと通信するためのクライアントクラスを提供します。
ECSのタスクを実行したり、タスクの実行結果を取得したりする機能を実装しています。
"""

import boto3
from typing import List, Dict

from src.infrastructure.utils.logger import get_logger
from src.application.schema.ecs_schema import TaskExecutionResult

logger = get_logger(__name__)


class EcsClient:
    def __init__(
        self,
        cluster_name: str,
        task_definition: str,
        container_name: str,
        security_group: str = None,
        subnet_id: str = None,
    ):
        """ECSクライアントの初期化

        Args:
            cluster_name (str): ECSクラスター名
            task_definition (str): タスク定義名
            container_name (str): コンテナ名
            security_group (str, optional): セキュリティグループID
            subnet_id (str, optional): サブネットID
        """
        self.ecs = boto3.client("ecs")
        self.cluster_name = cluster_name
        self.task_definition = task_definition
        self.container_name = container_name
        self.security_group = security_group
        self.subnet_id = subnet_id

    def run_task(
        self,
        task_definition: str = None,
        container_overrides: dict = None,
        environment: List[Dict[str, str]] = None,
    ) -> str:
        """タスクを実行する

        Args:
            task_definition (str, optional): タスク定義名。指定しない場合はコンストラクタで設定した値を使用
            container_overrides (dict, optional): コンテナのオーバーライド設定
            environment (List[Dict[str, str]], optional): 環境変数のリスト [{'name': 'VAR_NAME', 'value': 'var_value'}, ...]

        Returns:
            str: タスクARN

        Raises:
            Exception: タスク実行に失敗した場合
        """
        try:
            # 使用するタスク定義を決定
            task_def = task_definition if task_definition else self.task_definition

            # ネットワーク設定を構築
            network_config = {"awsvpcConfiguration": {"assignPublicIp": "DISABLED"}}

            # セキュリティグループとサブネットが設定されている場合は追加
            if self.security_group:
                network_config["awsvpcConfiguration"]["securityGroups"] = [
                    self.security_group
                ]

            if self.subnet_id:
                network_config["awsvpcConfiguration"]["subnets"] = [self.subnet_id]

            # タスク実行パラメータを構築
            params = {
                "cluster": self.cluster_name,
                "taskDefinition": task_def,
                "count": 1,
                "launchType": "FARGATE",
                "platformVersion": "LATEST",
                "networkConfiguration": network_config,
            }

            # コンテナのオーバーライド設定がある場合は追加
            if container_overrides:
                params["overrides"] = {"containerOverrides": [container_overrides]}
            # 環境変数が指定されている場合、オーバーライド設定に追加
            elif environment:
                params["overrides"] = {
                    "containerOverrides": [
                        {"name": self.container_name, "environment": environment}
                    ]
                }

            # タスクを実行
            response = self.ecs.run_task(**params)

            # タスクARNを取得して返す
            if "tasks" in response and len(response["tasks"]) > 0:
                return response["tasks"][0]["taskArn"]
            else:
                raise Exception(
                    "タスクの実行に成功しましたが、タスク情報を取得できませんでした"
                )

        except Exception as e:
            logger.error(f"ECSタスク実行エラー: {str(e)}")
            raise e

    def execute_task(
        self,
        task_definition: str | None,
        container_overrides: dict | None,
        environment: list[dict[str, str]] | None,
    ) -> TaskExecutionResult:
        """タスクを実行し、結果オブジェクトを返す

        Args:
            task_definition (str, optional): タスク定義名。指定しない場合はコンストラクタで設定した値を使用
            container_overrides (dict, optional): コンテナのオーバーライド設定
            environment (List[Dict[str, str]], optional): 環境変数のリスト [{'name': 'VAR_NAME', 'value': 'var_value'}, ...]

        Returns:
            TaskExecutionResult: タスク実行結果オブジェクト

        Raises:
            Exception: タスク実行に失敗した場合
        """
        task_arn = self.run_task(task_definition, container_overrides, environment)

        return TaskExecutionResult(task_arn=task_arn, cluster_name=self.cluster_name)
