import unittest
from unittest.mock import MagicMock, patch

import requests

from src.agent.function.open_url import OpenUrlFunction


class TestOpenUrlFunction(unittest.TestCase):
    """OpenUrlFunctionのテストクラス"""

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_normal_case(self, mock_get):
        """通常の短いコンテンツのURLを処理するケースのテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>テストページ</title></head><body>テストコンテンツ</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 関数実行
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="テスト情報"
        )

        # 結果の検証
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "テストページ")
        self.assertIn("テストコンテンツ", result["page_content"])
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("src.agent.function.open_url.requests.get")
    @patch("src.agent.function.open_url.AzureOpenAIClient")
    def test_execute_long_content_case(self, mock_azure_client, mock_get):
        """長いコンテンツのURLを処理するケースのテスト"""
        # モックの設定 - 長いコンテンツを生成
        mock_response = MagicMock()
        mock_response.text = (
            "<html><head><title>長いページ</title></head><body>"
            + "テスト" * 10000
            + "</body></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Azure OpenAI クライアントのモック
        mock_chat = MagicMock()
        mock_chat.invoke.return_value = MagicMock(content="要約されたコンテンツ")
        mock_azure_client.return_value.initialize_chat.return_value = mock_chat

        # 関数実行
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="長い情報"
        )

        # 結果の検証
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "長いページ")
        self.assertIn("要約されたコンテンツ", result["page_content"])
        mock_get.assert_called_once_with("https://example.com", timeout=10)
        self.assertTrue(mock_chat.invoke.called)

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_http_error(self, mock_get):
        """HTTPエラーが発生した場合のテスト"""
        # モックの設定 - HTTPエラーを発生させる
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # エラーが発生することを検証
        with self.assertRaises(requests.HTTPError):
            OpenUrlFunction.execute(
                url="https://example.com/not-found",
                what_i_want_to_know="存在しない情報",
            )

    @patch("src.agent.function.open_url.requests.get")
    def test_execute_no_title(self, mock_get):
        """タイトルがないHTMLを処理するケースのテスト"""
        # モックの設定 - タイトルなしのHTML
        mock_response = MagicMock()
        mock_response.text = "<html><body>タイトルなしのコンテンツ</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 関数実行
        result = OpenUrlFunction.execute(
            url="https://example.com", what_i_want_to_know="情報"
        )

        # 結果の検証
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["title"], "")
        self.assertIn("タイトルなしのコンテンツ", result["page_content"])

    @patch("src.agent.function.open_url.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_toolメソッドのテスト"""
        # モックを設定
        mock_tool = MagicMock()
        mock_tool.name = "open_url_function"
        mock_tool.description = "指定されたURLを開き、ページ内容を取得して要約します。"
        mock_from_function.return_value = mock_tool

        # 関数実行
        tool = OpenUrlFunction.to_tool()

        # 結果検証
        self.assertEqual(tool.name, "open_url_function")
        self.assertEqual(
            tool.description, "指定されたURLを開き、ページ内容を取得して要約します。"
        )

        # from_functionが正しいパラメータで呼ばれたことを確認
        mock_from_function.assert_called_once()
        # 名前が正しく渡されたか確認（BaseFunction.function_nameの挙動をモックで回避）
        args, kwargs = mock_from_function.call_args
        self.assertEqual(kwargs["func"], OpenUrlFunction.execute)
        self.assertEqual(
            kwargs["description"],
            "指定されたURLを開き、ページ内容を取得して要約します。",
        )


if __name__ == "__main__":
    unittest.main()
