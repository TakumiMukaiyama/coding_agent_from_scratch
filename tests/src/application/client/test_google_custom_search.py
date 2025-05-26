"""
GoogleSearchClientクラスの単体テストモジュール

GoogleカスタムサーチAPIを利用するクライアントクラスのテストを行う
"""

import unittest
from unittest.mock import MagicMock, patch

from src.application.client.google_search_client import GoogleSearchClient


class TestGoogleSearchClient(unittest.TestCase):
    """GoogleSearchClientクラスのテストケース"""

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def setUp(self, mock_settings, mock_build):
        """テスト前の準備を行う"""
        # 設定値のモック
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # buildのモック
        self.mock_service = MagicMock()
        mock_build.return_value = self.mock_service

        # テスト対象のインスタンス作成
        self.client = GoogleSearchClient()

        # buildが正しく呼び出されていないことを確認（初期化時には呼び出されない）
        mock_build.assert_not_called()

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_get_service(self, mock_settings, mock_build):
        """get_serviceメソッドのテスト"""
        # 設定値のモック
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # buildのモック
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # テスト対象のインスタンス作成
        client = GoogleSearchClient()

        # get_serviceを呼び出し
        service = client.get_service()

        # buildが正しく呼び出されたことを確認
        mock_build.assert_called_once_with(
            "customsearch",
            "v1",
            developerKey="test_api_key",
        )

        # 同じサービスが返されることを確認
        self.assertEqual(service, mock_service)

        # 2回目の呼び出しではbuildが呼ばれないことを確認
        service = client.get_service()
        mock_build.assert_called_once()  # 呼び出し回数が変わらないことを確認

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_search(self, mock_settings, mock_build):
        """searchメソッドのテスト"""
        # 設定値のモック
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # モックの準備
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # 戻り値の設定
        mock_execute.return_value = {"items": [{"title": "テスト結果"}]}
        mock_list.execute.return_value = mock_execute.return_value
        mock_cse.list.return_value = mock_list
        mock_service = MagicMock()
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # テスト対象のインスタンス作成
        client = GoogleSearchClient()

        # 検索実行
        result = client.search("テスト検索", num=5, start=2)

        # buildが正しく呼び出されたことを確認
        mock_build.assert_called_once_with(
            "customsearch",
            "v1",
            developerKey="test_api_key",
        )

        # listメソッドが正しく呼び出されたことを確認
        mock_cse.list.assert_called_once_with(
            q="テスト検索",
            cx="test_cx_id",
            lr="lang_ja",
            num=5,
            start=2,
        )

        # executeが呼び出されたことを確認
        mock_list.execute.assert_called_once()

        # 結果が正しいことを確認
        self.assertEqual(result, {"items": [{"title": "テスト結果"}]})

    @patch("src.application.client.google_search_client.build")
    @patch("src.application.client.google_search_client.google_search_settings")
    def test_search_with_default_params(self, mock_settings, mock_build):
        """デフォルトパラメータでのsearchメソッドのテスト"""
        # 設定値のモック
        mock_settings.GOOGLE_API_KEY = "test_api_key"
        mock_settings.CUSTOM_SEARCH_ENGINE_ID = "test_cx_id"

        # モックの準備
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # 戻り値の設定
        mock_execute.return_value = {"items": [{"title": "テスト結果"}]}
        mock_list.execute.return_value = mock_execute.return_value
        mock_cse.list.return_value = mock_list
        mock_service = MagicMock()
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # テスト対象のインスタンス作成
        client = GoogleSearchClient()

        # デフォルトパラメータで検索実行
        result = client.search("テスト検索")

        # listメソッドが正しく呼び出されたことを確認（デフォルトパラメータ）
        mock_cse.list.assert_called_once_with(
            q="テスト検索",
            cx="test_cx_id",
            lr="lang_ja",
            num=10,  # デフォルト値
            start=1,  # デフォルト値
        )

        # 結果が正しいことを確認
        self.assertEqual(result, {"items": [{"title": "テスト結果"}]})


if __name__ == "__main__":
    unittest.main()
