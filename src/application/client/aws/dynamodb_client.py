import boto3
from src.infrastructure.config.aws_setting import aws_settings
from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class DynamodbClient:
    """DynamoDBクライアント."""

    def __init__(self, table_name: str):
        """DynamoDBクライアントの初期化.

        Args:
            table_name (str): DynamoDBテーブル名
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=aws_settings.REGION)
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, key: dict) -> dict:
        """指定されたキーに一致するアイテムを取得します.

        Args:
            key (dict): 取得するアイテムのキー（例: {"session_id": "123"}）

        Returns:
            dict: 取得したアイテムのデータ、存在しない場合は空の辞書
        """
        response = self.table.get_item(Key=key)
        return response.get("Item", {})

    def put_item(self, item: dict) -> None:
        """指定されたアイテムをDynamoDBテーブルに挿入します.

        Args:
            item (dict): 挿入するアイテムのデータ
        """
        self.table.put_item(Item=item)

    def update_item(
        self,
        key: dict,
        update_expression: str,
        expression_attribute_values: dict,
        expression_attribute_names: dict = None,
    ) -> None:
        """指定されたキーに基づいてDynamoDBテーブルのアイテムを更新します.

        Args:
            key (dict): 更新するアイテムのキー（例: {"session_id": "123"}）
            update_expression (str): 更新式
            expression_attribute_values (dict): 更新式の属性値
            expression_attribute_names (dict, optional): 属性名のマッピング（予約語を使用する場合など）
        """
        params = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }

        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names

        self.table.update_item(**params)

    def delete_item(self, key: dict) -> None:
        """指定されたキーに基づいてDynamoDBテーブルのアイテムを削除します.

        Args:
            key (dict): 削除するアイテムのキー（例: {"session_id": "123"}）
        """
        self.table.delete_item(Key=key)

    def scan(
        self,
        filter_expression: str = None,
        expression_attribute_values: dict = None,
    ) -> list:
        """指定されたフィルター式と属性値に基づいてDynamoDBテーブルをスキャンします.

        フィルター式を指定しない場合はテーブル全体をスキャンします.

        Args:
            filter_expression (str, optional): フィルター式
            expression_attribute_values (dict, optional): フィルター式の属性値

        Returns:
            list: アイテムのリスト
        """
        params = {}
        if filter_expression:
            params["FilterExpression"] = filter_expression
        if expression_attribute_values:
            params["ExpressionAttributeValues"] = expression_attribute_values

        response = self.table.scan(**params)
        return response.get("Items", [])
