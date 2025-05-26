"""
GetFilesListFunctionの単体テスト
"""

import unittest
from unittest.mock import patch

from src.agent.function.get_files_list import GetFilesListFunction
from src.agent.schema.get_files_list_input import GetFilesListInput


class TestGetFilesListFunction(unittest.TestCase):
    """GetFilesListFunctionのテストクラス"""

    @patch("src.agent.function.get_files_list.glob.glob")
    def test_execute(self, mock_glob):
        """execute メソッドのテスト"""
        # モックの設定
        mock_glob.side_effect = lambda pattern, recursive: {
            "**/*.rb": ["file1.rb", "dir/file2.rb"],
            "**/*.yml": ["config.yml", "dir/settings.yml"],
        }[pattern]

        # テスト実行
        result = GetFilesListFunction.execute()

        # 検証
        self.assertEqual(mock_glob.call_count, 2)
        mock_glob.assert_any_call("**/*.rb", recursive=True)
        mock_glob.assert_any_call("**/*.yml", recursive=True)
        self.assertEqual(
            result,
            {
                "files_list": [
                    "file1.rb",
                    "dir/file2.rb",
                    "config.yml",
                    "dir/settings.yml",
                ]
            },
        )

    @patch("src.agent.function.get_files_list.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            GetFilesListFunction,
            "function_name",
            return_value="get_files_list_function",
        ):
            result = GetFilesListFunction.to_tool()

        # 検証
        mock_from_function.assert_called_once_with(
            name="get_files_list_function",
            description="プロジェクト配下の.pyファイルおよび.ymlファイル一覧を取得します。",
            func=GetFilesListFunction.execute,
            args_schema=GetFilesListInput,
        )
        self.assertEqual(result, "mock_tool")


if __name__ == "__main__":
    unittest.main()
