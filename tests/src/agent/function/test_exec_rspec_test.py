"""
ExecRspecTestFunctionの単体テスト
"""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.function.exec_rspec_test import ExecRspecTestFunction
from src.agent.schema.exec_rspec_test_input import ExecRspecTestInput


class TestExecRspecTestFunction(unittest.TestCase):
    """ExecRspecTestFunctionのテストクラス"""

    @patch("src.agent.function.exec_rspec_test.subprocess.run")
    def test_execute_success(self, mock_run):
        """execute メソッドが成功した場合のテスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.stdout = "テスト成功のメッセージ"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # テスト実行
        file_path = "spec/test_spec.rb"
        result = ExecRspecTestFunction.execute(file_path)

        # 検証
        mock_run.assert_called_once_with(
            f"bundle exec rspec '{file_path}'",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result["stdout"], "テスト成功のメッセージ")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["exit_status"], "0")

    @patch("src.agent.function.exec_rspec_test.subprocess.run")
    def test_execute_error(self, mock_run):
        """execute メソッドがエラーを発生させた場合のテスト"""
        # モックの設定
        from subprocess import CalledProcessError

        mock_error = CalledProcessError(1, "bundle exec rspec 'spec/test_spec.rb'")
        mock_error.stdout = "エラー出力"
        mock_error.stderr = "スタックトレース"
        mock_run.side_effect = mock_error

        # テスト実行
        file_path = "spec/test_spec.rb"
        result = ExecRspecTestFunction.execute(file_path)

        # 検証
        mock_run.assert_called_once_with(
            f"bundle exec rspec '{file_path}'",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result["stdout"], "エラー出力")
        self.assertEqual(result["stderr"], "スタックトレース")
        self.assertEqual(result["exit_status"], "1")

    @patch("src.agent.function.exec_rspec_test.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            ExecRspecTestFunction,
            "function_name",
            return_value="exec_rspec_test_function",
        ):
            result = ExecRspecTestFunction.to_tool()

        # 検証
        mock_from_function.assert_called_once_with(
            name="exec_rspec_test_function",
            description="指定したファイルまたはディレクトリに対してRSpecテストを実行します。",
            func=ExecRspecTestFunction.execute,
            args_schema=ExecRspecTestInput,
        )
        self.assertEqual(result, "mock_tool")


if __name__ == "__main__":
    unittest.main()
