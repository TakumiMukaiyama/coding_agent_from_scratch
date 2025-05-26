"""
GoogleSearchFunctionの単体テスト
"""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.function.google_search import GoogleSearchFunction
from src.agent.schema.google_search_input import GoogleSearchInput
from src.application.client.google_search_client import GoogleSearchClient


class TestGoogleSearchFunction(unittest.TestCase):
    """GoogleSearchFunctionのテストクラス"""

    @patch("src.agent.function.google_search.GoogleSearchFunction.search_client")
    def test_execute(self, mock_search_client):
        """execute メソッドのテスト"""
        # モックの設定
        mock_item1 = {
            "title": "テスト結果1",
            "formatted_url": "https://example.com/1",
            "html_snippet": "テストの内容1",
        }

        mock_item2 = {
            "title": "テスト結果2",
            "formatted_url": "https://example.com/2",
            "html_snippet": "テストの内容2",
        }

        mock_result = {"items": [mock_item1, mock_item2]}

        mock_client = MagicMock(spec=GoogleSearchClient)
        mock_client.search.return_value = mock_result
        mock_search_client.return_value = mock_client

        # テスト実行
        search_word = "テスト検索ワード"
        result = GoogleSearchFunction.execute(search_word)

        # 検証
        mock_client.search.assert_called_once_with(search_word, gl="jp")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "テスト結果1")
        self.assertEqual(result[0]["url"], "https://example.com/1")
        self.assertEqual(result[0]["snippet"], "テストの内容1")
        self.assertEqual(result[1]["title"], "テスト結果2")
        self.assertEqual(result[1]["url"], "https://example.com/2")
        self.assertEqual(result[1]["snippet"], "テストの内容2")

    @patch("src.agent.function.google_search.GoogleSearchClient")
    def test_search_client(self, mock_client_class):
        """search_client メソッドのテスト"""
        # クラス変数をリセット
        GoogleSearchFunction._search_client = None

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # 1回目の呼び出し
        client1 = GoogleSearchFunction.search_client()
        mock_client_class.assert_called_once()

        # 2回目の呼び出し（新しいインスタンスは作成されない）
        client2 = GoogleSearchFunction.search_client()
        mock_client_class.assert_called_once()  # 呼び出し回数は変わらない

        # 同じインスタンスが返されることを確認
        self.assertEqual(client1, client2)

    @patch("src.agent.function.google_search.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        mock_tool = MagicMock()
        mock_from_function.return_value = mock_tool

        # function_nameをモック化して、エラーを回避
        with patch.object(
            GoogleSearchFunction, "function_name", return_value="google_search_function"
        ):
            tool = GoogleSearchFunction.to_tool()

        mock_from_function.assert_called_once_with(
            name="google_search_function",
            description="指定されたキーワードでGoogle検索を実行し、結果を返します。",
            func=GoogleSearchFunction.execute,
            args_schema=GoogleSearchInput,
        )
        self.assertEqual(tool, mock_tool)


if __name__ == "__main__":
    unittest.main()
