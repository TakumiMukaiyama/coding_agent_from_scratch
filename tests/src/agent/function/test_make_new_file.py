"""
MakeNewFileFunctionの単体テスト
"""

import unittest
from unittest.mock import mock_open, patch

from src.agent.function.make_new_file import MakeNewFileFunction
from src.agent.schema.make_new_file_input import MakeNewFileInput


class TestMakeNewFileFunction(unittest.TestCase):
    """MakeNewFileFunctionのテストクラス"""

    @patch("src.agent.function.make_new_file.os.path.exists")
    @patch("src.agent.function.make_new_file.os.makedirs")
    @patch("src.agent.function.make_new_file.open", new_callable=mock_open)
    def test_execute_with_existing_directory(
        self, mock_file, mock_makedirs, mock_exists
    ):
        """既存ディレクトリにファイルを作成するテスト"""
        # モックの設定
        mock_exists.return_value = True

        # テスト実行
        filepath = "existing_dir/test_file.txt"
        file_contents = "テストコンテンツ"
        result = MakeNewFileFunction.execute(
            filepath=filepath, file_contents=file_contents
        )

        # 検証
        mock_exists.assert_called_once_with("existing_dir")
        mock_makedirs.assert_not_called()  # 既存ディレクトリなので作成されない
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(file_contents)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.make_new_file.os.path.exists")
    @patch("src.agent.function.make_new_file.os.makedirs")
    @patch("src.agent.function.make_new_file.open", new_callable=mock_open)
    def test_execute_with_new_directory(self, mock_file, mock_makedirs, mock_exists):
        """新規ディレクトリにファイルを作成するテスト"""
        # モックの設定
        mock_exists.return_value = False

        # テスト実行
        filepath = "new_dir/test_file.txt"
        file_contents = "テストコンテンツ"
        result = MakeNewFileFunction.execute(
            filepath=filepath, file_contents=file_contents
        )

        # 検証
        mock_exists.assert_called_once_with("new_dir")
        mock_makedirs.assert_called_once_with("new_dir", exist_ok=True)
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(file_contents)
        self.assertEqual(result, {"result": "success"})

    @patch("src.agent.function.make_new_file.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            MakeNewFileFunction, "function_name", return_value="make_new_file"
        ):
            result = MakeNewFileFunction.to_tool()

        # 検証
        mock_from_function.assert_called_once_with(
            name="make_new_file",
            description="新しいファイルを作成し、指定された内容で書き込みます。",
            func=MakeNewFileFunction.execute,
            args_schema=MakeNewFileInput,
        )
        self.assertEqual(result, "mock_tool")


def test_execute_with_real_filesystem(tmp_path):
    """実際のファイルシステムを使用したテスト"""
    # テストディレクトリとファイルのパスを設定
    test_dir = tmp_path / "test_dir"
    test_file = test_dir / "test_file.txt"
    file_contents = "テスト用コンテンツ"

    # 関数を実行
    result = MakeNewFileFunction.execute(
        filepath=str(test_file), file_contents=file_contents
    )

    # 検証
    assert result == {"result": "success"}
    assert test_dir.exists()  # ディレクトリが作成されたか
    assert test_file.exists()  # ファイルが作成されたか
    assert test_file.read_text(encoding="utf-8") == file_contents  # 内容が正しいか


if __name__ == "__main__":
    unittest.main()
