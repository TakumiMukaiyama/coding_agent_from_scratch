import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    """
    Slack API設定を保持するモデル

    Attributes:
        SLACK_SIGNING_SECRET_PARAM (str): Slackリクエスト署名検証用シークレットのパラメータ名
        SLACK_BOT_USER_OAUTH_TOKEN_PARAM (str): SlackボットユーザーOAuthトークンのパラメータ名
    """

    SLACK_SIGNING_SECRET: str = ""
    SLACK_BOT_USER_OAUTH_TOKEN: str = ""
    SLACK_SIGNING_SECRET_PARAM: str = ""
    SLACK_BOT_USER_OAUTH_TOKEN_PARAM: str = ""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        env_file_encoding="utf-8",
    )


# シングルトンインスタンスを作成
slack_settings = SlackSettings()
