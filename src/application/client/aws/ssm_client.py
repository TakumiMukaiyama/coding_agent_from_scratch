"""
AWS SSM Parameterストアからパラメータを取得するためのクライアント

AWSのSSMパラメータストアからパラメータを取得するための機能を提供します。
"""

import boto3
from typing import Dict, List

from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class SsmClient:
    """
    AWS SSM Parameterストアとの通信を行うクライアントクラス

    SSMパラメータストアからパラメータ値を取得するための機能を提供します。
    """

    def __init__(self):
        pass

    @classmethod
    def get_parameters(cls, param_names: List[str]) -> Dict[str, str]:
        """
        AWS SSM Parameterから複数の値を一度に取得します。

        Args:
            param_names (List[str]): SSMパラメータ名のリスト

        Returns:
            Dict[str, str]: パラメータ名をキー、値を値とする辞書
        """
        result = {}
        try:
            logger.info(f"SSMパラメータを取得します: {param_names}")
            ssm_client = boto3.client("ssm")
            response = ssm_client.get_parameters(Names=param_names, WithDecryption=True)

            # 取得したパラメータを辞書に格納
            for param in response["Parameters"]:
                name = param["Name"]
                value = param["Value"]
                result[name] = value
                value_length = len(value) if value else 0
                logger.info(f"SSMパラメータ取得成功: {name}, 値の長さ={value_length}")

            # 取得できなかったパラメータの出力
            if response.get("InvalidParameters"):
                logger.warning(
                    f"取得できなかったSSMパラメータ: {response['InvalidParameters']}"
                )

            return result
        except Exception as e:
            logger.error(f"SSMパラメータ取得エラー: {str(e)}")
            return result
