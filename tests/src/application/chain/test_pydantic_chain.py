"""
PydanticChainクラスの単体テストモジュール

このモジュールでは、PydanticChainクラスの各メソッドに対する単体テストを実装しています。
"""

import unittest
from unittest.mock import MagicMock, patch

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.application.chain.pydantic_chain import PydanticChain
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.dependency.chaindependency import ChainDependency
from src.application.schema.base import BaseInput, BaseOutput


class DummyInput(BaseInput):
    """テスト用のInput"""

    test_field: str


class DummyOutput(BaseOutput):
    """テスト用のOutput"""

    result: str


class TestPydanticChain(unittest.TestCase):
    """PydanticChainクラスのテストケース"""

    def setUp(self):
        """テスト前の準備"""
        # 必要なモックオブジェクトを作成
        self.mock_chat_llm = MagicMock(spec=ChatOpenAI)

        # ChainDependencyのモック作成
        self.mock_chain_dependency = MagicMock(spec=ChainDependency)
        self.mock_chain_dependency.get_output_schema.return_value = DummyOutput
        self.mock_chain_dependency.get_prompt_template.return_value = (
            "テストプロンプト {test_field}"
        )
        self.mock_chain_dependency.get_input_variables.return_value = ["test_field"]

        # PydanticChainインスタンスの作成
        self.chain = PydanticChain(
            chat_llm=self.mock_chat_llm,
            chain_dependency=self.mock_chain_dependency,
        )

        # テスト用の入力データ
        self.test_input = DummyInput(test_field="テスト値")

        # モックチェーンの設定
        self.mock_chain = MagicMock()
        self.chain.chain = self.mock_chain

    def test_init(self):
        """初期化メソッドのテスト"""
        # 期待値の確認
        self.assertEqual(self.chain.output_schema, DummyOutput)
        self.assertEqual(self.chain.chat_llm, self.mock_chat_llm)

        # プロンプトが正しく初期化されたことを確認
        self.assertIsInstance(self.chain.prompt, PromptTemplate)
        self.assertEqual(self.chain.prompt.template, "テストプロンプト {test_field}")
        self.assertEqual(self.chain.prompt.input_variables, ["test_field"])

    def test_get_prompt(self):
        """get_promptメソッドのテスト"""
        # モックの設定
        mock_prompt_template = MagicMock()
        mock_prompt_invoke_result = MagicMock()
        mock_prompt_template.invoke.return_value = mock_prompt_invoke_result
        mock_prompt_invoke_result.to_string.return_value = "テストプロンプト テスト値"

        self.chain.prompt = mock_prompt_template

        # メソッド実行
        result = self.chain.get_prompt(self.test_input)

        # 期待値の確認
        mock_prompt_template.invoke.assert_called_once_with({"test_field": "テスト値"})
        mock_prompt_invoke_result.to_string.assert_called_once()
        self.assertEqual(result, "テストプロンプト テスト値")

    def test_invoke(self):
        """invokeメソッドのテスト"""
        # モックの設定
        expected_result = {"result": "テスト結果"}
        self.mock_chain.invoke.return_value = expected_result

        # メソッド実行
        result = self.chain.invoke(self.test_input)

        # 期待値の確認
        self.mock_chain.invoke.assert_called_once_with({"test_field": "テスト値"})
        self.assertEqual(result, expected_result)

    @patch("time.sleep")
    def test_invoke_with_retry_no_error(self, mock_sleep):
        """エラーが発生しない場合のinvoke_with_retryメソッドのテスト"""
        # モックの設定
        expected_result = {"result": "テスト結果"}
        self.mock_chain.invoke.return_value = expected_result

        # モックLLMクライアント
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # メソッド実行
        result = self.chain.invoke_with_retry(
            self.test_input, llm_client=mock_llm_client
        )

        # 期待値の確認
        self.mock_chain.invoke.assert_called_once_with({"test_field": "テスト値"})
        self.assertEqual(result, expected_result)
        # sleepは呼ばれないはず
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_invoke_with_retry_rate_limit_error(self, mock_sleep):
        """レート制限エラーが発生した場合のinvoke_with_retryメソッドのテスト"""
        # 初回はレート制限エラーを発生させ、2回目は成功
        self.mock_chain.invoke.side_effect = [
            Exception("Rate limit exceeded"),
            {"result": "テスト結果"},
        ]

        # モックLLMクライアント
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # メソッド実行
        result = self.chain.invoke_with_retry(
            self.test_input, llm_client=mock_llm_client
        )

        # 期待値の確認
        self.assertEqual(self.mock_chain.invoke.call_count, 2)
        self.assertEqual(result, {"result": "テスト結果"})
        # sleepが1回呼ばれるはず
        mock_sleep.assert_called_once_with(60)

    @patch("time.sleep")
    def test_invoke_with_retry_max_retries_exceeded(self, mock_sleep):
        """最大リトライ回数を超えた場合のinvoke_with_retryメソッドのテスト"""
        # すべての試行でレート制限エラーを発生
        rate_limit_error = Exception("Rate limit exceeded")
        self.mock_chain.invoke.side_effect = rate_limit_error

        # モックLLMクライアント
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # メソッド実行（エラーが発生するはず）
        with self.assertRaises(Exception) as context:
            self.chain.invoke_with_retry(
                self.test_input, max_retries=3, llm_client=mock_llm_client
            )

        # 期待値の確認
        self.assertEqual(self.mock_chain.invoke.call_count, 3)  # 初回+2回リトライ
        self.assertEqual(mock_sleep.call_count, 2)  # 2回のリトライでsleepが2回呼ばれる
        self.assertEqual(context.exception, rate_limit_error)

    @patch("time.sleep")
    def test_invoke_with_retry_other_error(self, mock_sleep):
        """レート制限以外のエラーが発生した場合のinvoke_with_retryメソッドのテスト"""
        # 通常のエラーを発生
        other_error = Exception("Other error")
        self.mock_chain.invoke.side_effect = other_error

        # モックLLMクライアント
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # メソッド実行（エラーが発生するはず）
        with self.assertRaises(Exception) as context:
            self.chain.invoke_with_retry(self.test_input, llm_client=mock_llm_client)

        # 期待値の確認
        self.mock_chain.invoke.assert_called_once()  # リトライなし
        mock_sleep.assert_not_called()  # sleepは呼ばれない
        self.assertEqual(context.exception, other_error)


if __name__ == "__main__":
    unittest.main()
