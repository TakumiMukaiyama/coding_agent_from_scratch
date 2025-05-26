from pydantic_settings import BaseSettings, SettingsConfigDict


class AwsSettings(BaseSettings):
    """AWSの設定情報.
    Attributes:
        CLUSTER_NAME (str): ECSクラスター名
        TASK_DEFINITION (str): ECSタスク定義名
        SUBNET_ID (str): サブネットID
        SECURITY_GROUP (str): セキュリティグループID
        DYNAMODB_TABLE_NAME (str): DynamoDBテーブル名
        CONTAINER_NAME (str): ECSコンテナ名
        S3_BUCKET_NAME (str): S3バケット名
    """

    CLUSTER_NAME: str = ""
    TASK_DEFINITION: str = ""
    SUBNET_ID: str = ""
    SECURITY_GROUP: str = ""
    DYNAMODB_TABLE_NAME: str = ""
    CONTAINER_NAME: str = "agent"
    S3_BUCKET_NAME: str = "staffhub-member-for-branchi"
    S3_KEY: str = "staffs_list.csv"
    REGION: str = "ap-northeast-1"
    SESSION_ID: str = ""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        env_file_encoding="utf-8",
    )


# シングルトンインスタンスを作成
aws_settings = AwsSettings()
