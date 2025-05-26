"""
SlackClientの単体テスト

このモジュールはSlackClientクラスのメソッドをテストします。
Slackの実際のAPIを呼び出すことなく、モックを使用して機能をテストします。
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from src.application.client.slack_client import SlackClient


class TestSlackClient(unittest.TestCase):
    """
    SlackClientクラスのテストケース
    """

    def setUp(self):
        """
        各テスト前の準備
        """
        # SlackClientのインスタンス化をパッチ
        self.token_patcher = patch(
            "src.application.client.slack_client.slack_setting"
        )
        self.mock_slack_setting = self.token_patcher.start()
        self.mock_slack_setting.SLACK_BOT_USER_OAUTH_TOKEN = "mock-token"

        # WebClientをモック化
        self.client_patcher = patch(
            "src.application.client.slack_client.WebClient"
        )
        self.mock_web_client = self.client_patcher.start()
        self.mock_client_instance = MagicMock()
        self.mock_web_client.return_value = self.mock_client_instance

        # ロガーをモック化
        self.logger_patcher = patch("src.application.client.slack_client.logger")
        self.mock_logger = self.logger_patcher.start()

        # SlackClientのインスタンスを作成
        self.slack_client = SlackClient()

    def tearDown(self):
        """
        各テスト後のクリーンアップ
        """
        self.token_patcher.stop()
        self.client_patcher.stop()
        self.logger_patcher.stop()

    def test_init(self):
        """
        初期化が正しく行われることをテスト
        """
        self.assertEqual(self.slack_client.token, "mock-token")
        self.mock_web_client.assert_called_once_with(token="mock-token")

    def test_send_message_success(self):
        """
        send_messageが成功した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"ok": True, "ts": "1234567890.123456"}
        self.mock_client_instance.chat_postMessage.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.send_message(
            channel="C12345", message="テストメッセージ"
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.chat_postMessage.assert_called_once_with(
            channel="C12345", text="テストメッセージ", blocks=None, thread_ts=None
        )
        self.mock_logger.info.assert_called_once()

    def test_send_message_with_blocks(self):
        """
        blocksを指定してsend_messageを呼び出した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"ok": True, "ts": "1234567890.123456"}
        self.mock_client_instance.chat_postMessage.return_value = expected_response

        # テスト用のブロック
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "テスト"}}]

        # メソッドを呼び出し
        response = self.slack_client.send_message(
            channel="C12345", message="テストメッセージ", blocks=blocks
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.chat_postMessage.assert_called_once_with(
            channel="C12345", text="テストメッセージ", blocks=blocks, thread_ts=None
        )

    def test_send_message_with_thread_ts(self):
        """
        thread_tsを指定してsend_messageを呼び出した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"ok": True, "ts": "1234567890.999999"}
        self.mock_client_instance.chat_postMessage.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.send_message(
            channel="C12345", message="テストメッセージ", thread_ts="1234567890.123456"
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.chat_postMessage.assert_called_once_with(
            channel="C12345",
            text="テストメッセージ",
            blocks=None,
            thread_ts="1234567890.123456",
        )

    def test_send_message_error(self):
        """
        send_messageでエラーが発生した場合のテスト
        """
        # SlackApiErrorを発生させる
        mock_error = SlackApiError("Error", {"error": "channel_not_found"})
        self.mock_client_instance.chat_postMessage.side_effect = mock_error

        # エラーが発生することを検証
        with pytest.raises(SlackApiError):
            self.slack_client.send_message(channel="C12345", message="テストメッセージ")

        self.mock_logger.error.assert_called_once()

    def test_send_thread_message_success(self):
        """
        send_thread_messageが成功した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"ok": True, "ts": "1234567890.999999"}
        self.mock_client_instance.chat_postMessage.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.send_thread_message(
            channel="C12345", thread_ts="1234567890.123456", message="スレッドへの返信"
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.chat_postMessage.assert_called_once_with(
            channel="C12345",
            text="スレッドへの返信",
            blocks=None,
            thread_ts="1234567890.123456",
        )
        self.mock_logger.info.assert_called_once()

    def test_send_thread_message_error(self):
        """
        send_thread_messageでエラーが発生した場合のテスト
        """
        # SlackApiErrorを発生させる
        mock_error = SlackApiError("Error", {"error": "thread_not_found"})
        self.mock_client_instance.chat_postMessage.side_effect = mock_error

        # エラーが発生することを検証
        with pytest.raises(SlackApiError):
            self.slack_client.send_thread_message(
                channel="C12345",
                thread_ts="1234567890.123456",
                message="スレッドへの返信",
            )

        self.mock_logger.error.assert_called_once()

    def test_verify_token_true(self):
        """
        verify_tokenがTrueを返す場合のテスト
        """
        result = self.slack_client.verify_token("mock-token")
        self.assertTrue(result)

    def test_verify_token_false(self):
        """
        verify_tokenがFalseを返す場合のテスト
        """
        result = self.slack_client.verify_token("wrong-token")
        self.assertFalse(result)

    def test_get_user_info_success(self):
        """
        get_user_infoが成功した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"user": {"id": "U12345", "name": "testuser"}}
        self.mock_client_instance.users_info.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.get_user_info(user_id="U12345")

        # 結果を検証
        self.assertEqual(response, expected_response["user"])
        self.mock_client_instance.users_info.assert_called_once_with(user="U12345")
        self.mock_logger.info.assert_called_once()

    def test_get_user_info_error(self):
        """
        get_user_infoでエラーが発生した場合のテスト
        """
        # SlackApiErrorを発生させる
        mock_error = SlackApiError("Error", {"error": "user_not_found"})
        self.mock_client_instance.users_info.side_effect = mock_error

        # エラーが発生することを検証
        with pytest.raises(SlackApiError):
            self.slack_client.get_user_info(user_id="U12345")

        self.mock_logger.error.assert_called_once()

    def test_upload_file_success(self):
        """
        upload_fileが成功した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {"ok": True, "file": {"id": "F12345"}}
        self.mock_client_instance.files_upload_v2.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.upload_file(
            channels="C12345", file_path="/path/to/file.txt", title="テストファイル"
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.files_upload_v2.assert_called_once_with(
            channels="C12345",
            file="/path/to/file.txt",
            title="テストファイル",
            initial_comment=None,
            thread_ts=None,
        )
        self.mock_logger.info.assert_called_once()

    def test_upload_file_error(self):
        """
        upload_fileでエラーが発生した場合のテスト
        """
        # SlackApiErrorを発生させる
        mock_error = SlackApiError("Error", {"error": "file_not_found"})
        self.mock_client_instance.files_upload_v2.side_effect = mock_error

        # エラーが発生することを検証
        with pytest.raises(SlackApiError):
            self.slack_client.upload_file(
                channels="C12345", file_path="/path/to/file.txt"
            )

        self.mock_logger.error.assert_called_once()

    def test_get_thread_messages_success(self):
        """
        get_thread_messagesが成功した場合のテスト
        """
        # モックの戻り値を設定
        expected_response = {
            "ok": True,
            "messages": [{"text": "メッセージ1"}, {"text": "メッセージ2"}],
        }
        self.mock_client_instance.conversations_replies.return_value = expected_response

        # メソッドを呼び出し
        response = self.slack_client.get_thread_messages(
            channel="C12345", thread_ts="1234567890.123456"
        )

        # 結果を検証
        self.assertEqual(response, expected_response)
        self.mock_client_instance.conversations_replies.assert_called_once_with(
            channel="C12345", ts="1234567890.123456"
        )
        self.mock_logger.info.assert_called_once()

    def test_get_thread_messages_error(self):
        """
        get_thread_messagesでエラーが発生した場合のテスト
        """
        # SlackApiErrorを発生させる
        mock_error = SlackApiError("Error", {"error": "thread_not_found"})
        self.mock_client_instance.conversations_replies.side_effect = mock_error

        # エラーが発生することを検証
        with pytest.raises(SlackApiError):
            self.slack_client.get_thread_messages(
                channel="C12345", thread_ts="1234567890.123456"
            )

        self.mock_logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
