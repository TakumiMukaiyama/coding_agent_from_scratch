import boto3

from src.application.client.slack_client import SlackClient
from src.infrastructure.config.slack_setting import (
    SlackSettingsModel,
    BOT_TOKEN_PARAM,
    SIGNING_SECRET_PARAM,
)
from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Slackクライアントのサンプル機能を実行するメイン関数
    """
    try:
        # SSMパラメータストアから値を取得
        ssm = boto3.client("ssm")
        signing_secret = ssm.get_parameter(
            Name=SIGNING_SECRET_PARAM, WithDecryption=True
        )["Parameter"]["Value"]
        bot_token = ssm.get_parameter(Name=BOT_TOKEN_PARAM, WithDecryption=True)[
            "Parameter"
        ]["Value"]

        # Slack設定モデルを生成
        slack_settings = SlackSettingsModel.from_ssm(
            signing_secret=signing_secret,
            bot_token=bot_token,
        )

        # Slackクライアントを初期化
        slack_client = SlackClient(slack_settings)

        # SlackのチャンネルID
        channel_id = "xxxxxxxx"

        # 1. 通常メッセージ送信
        message = "こんにちは！これはSlackクライアントのテストメッセージです。"
        logger.info("基本的なメッセージを送信します...")
        response = slack_client.send_message(channel=channel_id, message=message)

        message_ts = response["ts"]
        logger.info(f"メッセージ送信完了。タイムスタンプ: {message_ts}")

        # 2. スレッドへの返信
        thread_message = "これはスレッドへの返信メッセージです。"
        logger.info(f"スレッド（{message_ts}）に返信します...")
        slack_client.send_thread_message(
            channel=channel_id, thread_ts=message_ts, message=thread_message
        )

        # 3. Block Kit メッセージ送信
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*リッチなメッセージ*\nBlock Kitを使った例です。",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "• リスト1\n• リスト2\n• リスト3"},
            },
        ]
        logger.info("Block Kitを使ったメッセージを送信します...")
        slack_client.send_message(
            channel=channel_id, message="リッチメッセージ", blocks=blocks
        )

        # 4. スレッドメッセージの取得
        logger.info(f"スレッド {message_ts} のメッセージを取得します...")
        thread_messages = slack_client.get_thread_messages(
            channel=channel_id, thread_ts=message_ts
        )
        logger.info(f"スレッド内のメッセージ数: {len(thread_messages['messages'])}")

        logger.info("すべてのテストが完了しました！")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    main()
