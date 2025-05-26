import unittest

from src.agent.function.record_lgtm import RecordLgtmFunction
from src.agent.schema.record_lgtm_input import RecordLgtmInput


class TestRecordLgtmFunction(unittest.TestCase):
    """RecordLgtmFunctionクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.function = RecordLgtmFunction()

    def test_init(self):
        """初期化後のlgtm状態がFalseであることを確認"""
        self.assertFalse(self.function.lgtm())

    def test_execute(self):
        """execute実行後、lgtm状態がTrueになることを確認"""
        result = self.function.execute()

        # 戻り値の確認
        self.assertEqual(result, {"result": "LGTMを記録しました"})

        # lgtm状態がTrueになっていることを確認
        self.assertTrue(self.function.lgtm())

    def test_to_tool(self):
        """to_toolメソッドがStructuredToolを返すことを確認"""
        tool = RecordLgtmFunction.to_tool()

        # ツール名の確認
        self.assertEqual(tool.name, "record_lgtm_function")

        # 引数スキーマの確認
        self.assertEqual(tool.args_schema, RecordLgtmInput)

        # ツールの説明文の確認
        self.assertIn("LGTM", tool.description)

    def test_tool_execution(self):
        """to_toolで生成されたツールが正常に実行できることを確認"""
        tool = RecordLgtmFunction.to_tool()

        # ツールを実行
        result = tool.invoke({})

        # 戻り値の確認
        self.assertEqual(result, {"result": "LGTMを記録しました"})


if __name__ == "__main__":
    unittest.main()
