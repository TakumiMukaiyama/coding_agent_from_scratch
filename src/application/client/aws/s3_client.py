"""
S3クライアントモジュール

このモジュールはAWS S3と通信するためのクライアントクラスを提供します。
S3バケットからオブジェクトの取得、アップロード、削除などの操作を行う機能を実装しています。
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import os
import pandas as pd
import io

from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class S3Client:
    def __init__(self, bucket_name: str):
        """S3クライアントの初期化

        Args:
            bucket_name (str): S3バケット名
        """
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def get_object(self, key: str) -> Optional[Dict[str, Any]]:
        """指定されたキーに一致するオブジェクトを取得します

        Args:
            key (str): 取得するオブジェクトのキー

        Returns:
            Optional[Dict[str, Any]]: 取得したオブジェクトのデータ、存在しない場合はNone

        Raises:
            Exception: オブジェクトの取得に失敗した場合
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"指定されたキーのオブジェクトが存在しません: {key}")
                return None
            else:
                logger.error(f"S3オブジェクト取得エラー: {str(e)}")
                raise e

    def download_file(self, key: str, local_path: str) -> bool:
        """S3からファイルをダウンロードします

        Args:
            key (str): ダウンロードするオブジェクトのキー
            local_path (str): ダウンロード先のローカルパス

        Returns:
            bool: ダウンロードが成功した場合はTrue、失敗した場合はFalse

        Raises:
            Exception: ファイルのダウンロードに失敗した場合
        """
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.s3.download_file(self.bucket_name, key, local_path)
            logger.info(f"ファイルをダウンロードしました: {key} -> {local_path}")
            return True
        except ClientError as e:
            logger.error(f"S3ファイルダウンロードエラー: {str(e)}")
            raise e

    def get_csv_as_dataframe(
        self, key: str, encoding: str = "utf-8", **kwargs
    ) -> Optional[pd.DataFrame]:
        """S3からCSVファイルを取得してDataFrameに変換します

        Args:
            key (str): 取得するCSVオブジェクトのキー
            encoding (str, optional): CSVファイルのエンコーディング。デフォルトは'utf-8'
            **kwargs: pandas.read_csvに渡す追加のパラメータ

        Returns:
            Optional[pd.DataFrame]: 読み込んだDataFrame、取得に失敗した場合はNone

        Raises:
            Exception: CSVの取得または変換に失敗した場合
        """
        try:
            # オブジェクトを取得
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            # レスポンスのBodyからCSVデータを読み込む
            csv_content = response["Body"].read().decode(encoding)
            # StringIOに変換してpandasで読み込む
            csv_buffer = io.StringIO(csv_content)
            df = pd.read_csv(csv_buffer, **kwargs)
            logger.info(
                f"CSVファイルをDataFrameに変換しました: {key}, サイズ: {df.shape}"
            )
            return df
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"指定されたキーのCSVファイルが存在しません: {key}")
                return None
            else:
                logger.error(f"S3 CSVファイル取得エラー: {str(e)}")
                raise e
        except Exception as e:
            logger.error(f"CSVのDataFrame変換エラー: {str(e)}")
            raise e
