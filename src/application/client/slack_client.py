"""
Slackクライアントモジュール

このモジュールはSlack APIと通信するためのクライアントクラスを提供します。
slack_sdkを使用してSlackにメッセージを送信したり、ユーザー情報を取得したりする機能を実装しています。
また、Slackからのリクエストの署名検証機能も提供します。
"""

from typing import Any

from src.infrastructure.utils.logger import get_logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

logger = get_logger(__name__)


class SlackClient:
    """
    SlackクライアントクラスはSlack APIとの通信を担当します。

    Attributes:
        client (WebClient): slack_sdkのWebClientインスタンス
        signature_verifier (SignatureVerifier): リクエスト署名を検証するためのverifierインスタンス
    """

    def __init__(self, signing_secret: str, bot_token: str):
        """
        Slackクライアントを初期化します。

        Args:
            signing_secret (str): Slackリクエスト署名検証用シークレット
            bot_token (str): SlackボットユーザーOAuthトークン
        """
        # Slack SDKクライアントを初期化
        self.client = WebClient(token=bot_token)
        self.signature_verifier = SignatureVerifier(signing_secret=signing_secret)

    def send_message(
        self,
        channel: str,
        message: str,
        blocks: list | None = None,
        thread_ts: str | None = None,
    ) -> dict[str, Any]:
        """
        指定されたチャンネルにメッセージを送信します。

        Args:
            channel (str): メッセージを送信するチャンネルID
            message (str): 送信するテキストメッセージ
            blocks (list | None): Block Kitフォーマットのメッセージ構造（省略可）
            thread_ts (str | None): スレッドのタイムスタンプ（返信として送信する場合）

        Returns:
            dict[str, Any]: Slack APIからのレスポンス

        Raises:
            SlackApiError: Slack APIとの通信中にエラーが発生した場合
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel, text=message, blocks=blocks, thread_ts=thread_ts
            )
            logger.info(
                f"メッセージ送信成功: チャンネル={channel}, スレッド={thread_ts if thread_ts else 'なし'}"
            )
            return response
        except SlackApiError as e:
            error_message = f"Slackメッセージ送信エラー: 関数=send_message, チャンネル={channel}, エラー={e.response['error']}"
            logger.error(error_message)
            raise

    def send_thread_message(
        self, channel: str, thread_ts: str, message: str, blocks: list | None = None
    ) -> dict[str, Any]:
        """
        特定のスレッドにメッセージを送信します。

        Args:
            channel (str): メッセージを送信するチャンネルID
            thread_ts (str): 返信するスレッドのタイムスタンプ
            message (str): 送信するテキストメッセージ
            blocks (list | None): Block Kitフォーマットのメッセージ構造（省略可）

        Returns:
            dict[str, Any]: Slack APIからのレスポンス

        Raises:
            SlackApiError: Slack APIとの通信中にエラーが発生した場合
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel, text=message, blocks=blocks, thread_ts=thread_ts
            )
            logger.info(
                f"スレッドへのメッセージ送信成功: チャンネル={channel}, スレッド={thread_ts}"
            )
            return response
        except SlackApiError as e:
            error_message = (
                f"スレッドへのメッセージ送信エラー: 関数=send_thread_message, チャンネル={channel}, "
                f"スレッド={thread_ts}, エラー={e.response['error']}"
            )
            logger.error(error_message)
            raise

    def verify_request(self, headers: dict[str, str], body: str | bytes) -> bool:
        """
        Slackからのリクエストの署名を検証します。

        Slackのリクエストにはx-slack-signatureとx-slack-request-timestampヘッダーが含まれており、
        これらを使用してリクエストの真正性を検証します。

        Args:
            headers (dict[str, str]): リクエストヘッダー
            body (str | bytes): リクエストボディ

        Returns:
            bool: 署名の検証が成功した場合はTrue、それ以外はFalse
        """
        try:
            if not self.signature_verifier:
                logger.error("署名検証エラー: 署名verifierが初期化されていません")
                return False

            # 大文字小文字を気にせずにヘッダーキーを取得
            signature = None
            timestamp = None
            for key, value in headers.items():
                if key.lower() == "x-slack-signature":
                    signature = value
                elif key.lower() == "x-slack-request-timestamp":
                    timestamp = value

            is_valid = self.signature_verifier.is_valid_request(
                body=body, headers=headers
            )
            if is_valid:
                logger.info("Slackリクエスト署名の検証に成功しました")
            else:
                logger.warning("Slackリクエスト署名の検証に失敗しました")
            return is_valid
        except Exception as e:
            error_message = f"署名検証エラー: 関数=verify_request, エラー={str(e)}"
            logger.error(error_message)
            return False

    def get_user_info(self, user_id: str) -> dict[str, Any]:
        """
        指定されたユーザーIDに関連する情報を取得します。

        Args:
            user_id (str): 情報を取得するSlackユーザーID

        Returns:
            dict[str, Any]: ユーザー情報を含む辞書

        Raises:
            SlackApiError: Slack APIとの通信中にエラーが発生した場合
        """
        try:
            response = self.client.users_info(user=user_id)
            logger.info(f"ユーザー情報取得成功: ユーザーID={user_id}")
            return response["user"]
        except SlackApiError as e:
            error_message = f"ユーザー情報取得エラー: 関数=get_user_info, ユーザーID={user_id}, エラー={e.response['error']}"
            logger.error(error_message)
            raise SlackApiError

    def get_thread_messages(self, channel: str, thread_ts: str) -> dict[str, Any]:
        """
        特定のスレッドのメッセージを取得します。

        Args:
            channel (str): チャンネルID
            thread_ts (str): スレッドのタイムスタンプ

        Returns:
            dict[str, Any]: スレッド内のメッセージを含むレスポンス

        Raises:
            SlackApiError: Slack APIとの通信中にエラーが発生した場合
        """
        try:
            response = self.client.conversations_replies(
                channel=channel, ts=thread_ts, inclusive=True
            )
            logger.info(
                f"スレッドメッセージ取得成功: チャンネル={channel}, スレッド={thread_ts}"
            )
            return response
        except SlackApiError as e:
            error_message = (
                f"スレッドメッセージ取得エラー: 関数=get_thread_messages, チャンネル={channel}, "
                f"スレッド={thread_ts}, エラー={e.response['error']}"
            )
            logger.error(error_message)
            raise SlackApiError

    def get_user_email_from_user_id(self, user_id: str) -> str:
        """
        指定されたユーザーIDに関連するメールアドレスを取得します。

        Args:
            user_id (str): メールアドレスを取得するSlackユーザーID

        Returns:
            str: ユーザーのメールアドレス

        Raises:
            SlackApiError: Slack APIとの通信中にエラーが発生した場合
        """
        try:
            response = self.client.users_info(user=user_id)
            logger.info(f"ユーザー情報取得成功: ユーザーID={user_id}")
            return response["user"]["profile"]["email"]
        except SlackApiError as e:
            logger.error(
                f"ユーザー情報取得エラー: 関数=get_user_email_from_user_id, ユーザーID={user_id}, エラー={e.response['error']}"
            )
            return "NONE"

    def get_real_name_from_user_id(self, user_id: str) -> str:
        """
        指定されたユーザーIDに関連する実名を取得します。

        Args:
            user_id (str): 実名を取得するSlackユーザーID

        Returns:
            str: ユーザーの実名
        """
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]["real_name"]
        except SlackApiError as e:
            logger.error(
                f"ユーザー情報取得エラー: 関数=get_real_name_from_user_id, ユーザーID={user_id}, エラー={e.response['error']}"
            )
            return "NONE"

    def get_reply_count(self, channel_id: str, thread_ts: str) -> int:
        """
        指定されたチャンネルとスレッドの返信数を取得します。

        Args:
            channel_id (str): チャンネルID
            thread_ts (str): スレッドのタイムスタンプ

        Returns:
            int: 返信数
        """
        try:
            response = self.get_thread_messages(channel_id, thread_ts)
            reply_count = response["messages"][0]["reply_count"]
            return reply_count
        except Exception:
            raise Exception("Error getting reply count")
