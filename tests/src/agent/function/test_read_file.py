import unittest
from unittest.mock import mock_open, patch

from src.agent.function.read_file import ReadFileFunction
from src.agent.schema.read_file_input import ReadFileInput


class TestReadFileFunction(unittest.TestCase):
    """
    ReadFileFunctionクラスのテストケース

    以下のケースをテストします：
    - ファイルが存在する場合の正常系
    - ファイルが存在しない場合のエラーハンドリング
    - to_tool関数の正常動作確認
    """

    def test_execute_file_exists(self):
        """ファイルが存在する場合のテスト"""
        file_content = "テストコンテンツ"
        filepath = "test_file.txt"

        # ファイルが開かれるときのモック
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=file_content)),
        ):
            result = ReadFileFunction.execute(filepath)

            self.assertEqual(result["filepath"], filepath)
            self.assertEqual(result["file_contents"], file_content)

    def test_execute_file_not_exists(self):
        """ファイルが存在しない場合のテスト"""
        filepath = "non_existent_file.txt"

        # ファイルが存在しないことをモック
        with patch("os.path.exists", return_value=False):
            result = ReadFileFunction.execute(filepath)

            self.assertEqual(result["filepath"], filepath)
            self.assertEqual(result["error"], "File not found.")

    def test_to_tool(self):
        """to_tool関数が正しくStructuredToolを返すことを確認"""
        tool = ReadFileFunction.to_tool()

        self.assertEqual(tool.name, "read_file_function")
        self.assertEqual(
            tool.description, "指定されたファイルを読み取り、内容を返します。"
        )
        self.assertEqual(tool.args_schema, ReadFileInput)


if __name__ == "__main__":
    unittest.main()
