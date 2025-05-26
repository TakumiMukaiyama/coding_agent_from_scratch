from src.usecase.reviewer.agent import ReviewerAgent
from src.agent.schema.reviewer_input import ReviewerInput


def test_normal_review():
    """通常のレビュー実行テスト"""
    # 簡単なダミー差分を用意
    dummy_diff = """
diff --git a/src/example.py b/src/example.py
index e69de29..b6fc4c9 100644
--- a/src/example.py
+++ b/src/example.py
@@ def example_function():
+    print("Hello, World!")
    """

    # プログラマーからの補足コメント
    programmer_comment = "簡単な出力テスト用の関数です。レビューをお願いします。"

    # 入力を構成
    reviewer_input = ReviewerInput(
        diff=dummy_diff, programmer_comment=programmer_comment
    )

    # エージェント実行
    agent = ReviewerAgent()
    output = agent.run(reviewer_input)

    # 結果出力
    print("""\n=== 通常レビューテスト ===\n""")
    print(f"Summary: {output.summary}\n")
    print(f"Suggestions: {output.suggestions}\n")
    print(f"LGTM: {output.lgtm}\n")


def test_lgtm_manually():
    """LGTM判定を手動で設定するテスト"""
    # 簡単なダミー差分を用意
    dummy_diff = """
diff --git a/src/example.py b/src/example.py
index e69de29..b6fc4c9 100644
--- a/src/example.py
+++ b/src/example.py
@@ def example_function():
+    # Call the function
+   def example_function():
+       print("Hello, World!")
+   example_function()
    """

    # 入力を構成
    reviewer_input = ReviewerInput(
        diff=dummy_diff, programmer_comment="良い実装です。承認してください。"
    )

    # エージェント実行
    agent = ReviewerAgent()

    # LGTMを手動で設定
    record_lgtm_tool = agent.record_lgtm_function
    record_lgtm_tool.set_lgtm(True)

    output = agent.run(reviewer_input)

    # 結果出力
    print("""\n=== LGTM手動設定テスト ===\n""")
    print(f"Summary: {output.summary}\n")
    print(f"Suggestions: {output.suggestions}\n")
    print(f"LGTM: {output.lgtm}\n")


def main():
    """メイン実行関数"""
    # 通常のレビューテスト
    test_normal_review()


if __name__ == "__main__":
    main()
