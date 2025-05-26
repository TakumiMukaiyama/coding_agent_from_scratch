"""
OverwriteFileFunctionの単体テスト
"""

import unittest
from unittest.mock import mock_open, patch

from src.agent.function.over_write_file import OverwriteFileFunction
from src.agent.schema.over_write_input import OverwriteFileInput


class TestOverwriteFileFunction(unittest.TestCase):
    """OverwriteFileFunctionのテストクラス"""

    @patch("src.agent.function.over_write_file.open", new_callable=mock_open)
    def test_execute(self, mock_file):
        """ファイルを上書きするテスト"""
        # テスト実行
        filepath = "test_dir/test_file.txt"
        new_text = "新しいテストコンテンツ"
        result = OverwriteFileFunction.execute(filepath=filepath, new_text=new_text)

        # 検証
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(new_text)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.over_write_file.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            OverwriteFileFunction, "function_name", return_value="overwrite_file"
        ):
            result = OverwriteFileFunction.to_tool()

        # 検証
        mock_from_function.assert_called_once_with(
            name="overwrite_file",
            description="指定されたファイルに対して新しい内容で上書きします。",
            func=OverwriteFileFunction.execute,
            args_schema=OverwriteFileInput,
        )
        self.assertEqual(result, "mock_tool")


def test_execute_with_real_filesystem(tmp_path):
    """実際のファイルシステムを使用したテスト"""
    # テストファイルのパスを設定
    test_file = tmp_path / "test_file.txt"

    # ファイルを初期内容で作成
    initial_content = "初期コンテンツ"
    test_file.write_text(initial_content, encoding="utf-8")

    # 上書き用の新しい内容
    new_content = "新しいコンテンツ"

    # 関数を実行
    result = OverwriteFileFunction.execute(
        filepath=str(test_file), new_text=new_content
    )

    # 検証
    assert result == {"result": "success"}
    assert test_file.exists()  # ファイルが存在するか
    assert test_file.read_text(encoding="utf-8") == new_content  # 内容が上書きされたか
    assert (
        test_file.read_text(encoding="utf-8") != initial_content
    )  # 初期内容ではないか


if __name__ == "__main__":
    unittest.main()
