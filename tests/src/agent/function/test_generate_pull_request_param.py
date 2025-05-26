"""
GeneratePullRequestParamsFunctionの単体テスト
"""

import unittest
from unittest.mock import patch

from src.agent.function.generate_pull_request_params import (
    GeneratePullRequestParamsFunction,
)
from src.agent.schema.generate_pull_request_params_input import (
    GeneratePullRequestParamsInput,
)


class TestGeneratePullRequestParamsFunction(unittest.TestCase):
    """GeneratePullRequestParamsFunctionのテストクラス"""

    def test_execute(self):
        """execute メソッドのテスト"""
        # テスト対象のインスタンスを作成
        function = GeneratePullRequestParamsFunction()

        # パラメータの準備
        title = "テストPRのタイトル"
        description = "テストPRの説明文"
        branch_name = "test/branch-name"

        # テスト実行
        result = function.execute(
            title=title, description=description, branch_name=branch_name
        )

        # 検証
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(function.title, title)
        self.assertEqual(function.description, description)
        self.assertEqual(function.branch_name, branch_name)

    @patch(
        "src.agent.function.generate_pull_request_params.StructuredTool.from_function"
    )
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            GeneratePullRequestParamsFunction,
            "function_name",
            return_value="generate_pull_request_params_function",
        ):
            result = GeneratePullRequestParamsFunction.to_tool()

        # 検証
        mock_from_function.assert_called_once()
        self.assertEqual(
            mock_from_function.call_args[1]["name"],
            "generate_pull_request_params_function",
        )
        self.assertEqual(
            mock_from_function.call_args[1]["description"],
            "Pull Requestのタイトル・説明・ブランチ名を生成します。",
        )
        # wrapperがパラメータとして渡されていることを確認
        self.assertTrue(callable(mock_from_function.call_args[1]["func"]))
        self.assertEqual(
            mock_from_function.call_args[1]["args_schema"],
            GeneratePullRequestParamsInput,
        )
        self.assertEqual(result, "mock_tool")

    def test_wrapper_functionality(self):
        """wrapper関数の機能テスト"""
        # モックを使用してwrapper関数を取得
        with (
            patch(
                "src.agent.function.generate_pull_request_params.StructuredTool.from_function"
            ) as mock_from_function,
            patch.object(
                GeneratePullRequestParamsFunction,
                "function_name",
                return_value="generate_pull_request_params_function",
            ),
        ):
            GeneratePullRequestParamsFunction.to_tool()
            wrapper_func = mock_from_function.call_args[1]["func"]

        # wrapperに渡される前後でインスタンスの状態が更新されることを確認
        result = wrapper_func(
            title="ラップされたタイトル",
            description="ラップされた説明",
            branch_name="wrapped/branch-name",
        )

        self.assertEqual(result, {"result": "success"})


if __name__ == "__main__":
    unittest.main()
