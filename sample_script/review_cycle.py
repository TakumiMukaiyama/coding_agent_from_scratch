from src.usecase.programmer.agent import ProgrammerAgent
from src.usecase.reviewer.agent import ReviewerAgent
from src.agent.schema.reviewer_input import ReviewerInput

MAX_REVIEW_LOOPS = 5


def main():
    # 最初の自然言語による指示
    instruction = (
        "簡単なPython関数を書いてください。例えば 'Hello, World!' を出力する関数など。"
    )

    programmer_agent = ProgrammerAgent()
    reviewer_agent = ReviewerAgent()

    reviewer_comment = None
    # diff = ""
    # lgtm = False

    for i in range(MAX_REVIEW_LOOPS):
        print(f"\n========== 🚀 Review Loop {i + 1} ==========\n")

        # Step 1: プログラマーが指示（とレビュー指摘）に基づいてコードを書く
        programmer_output = programmer_agent.run(
            instruction, reviewer_comment=reviewer_comment
        )
        print(f"\n👨‍💻 ProgrammerAgent Output:\n{programmer_output}")

        # 実際の差分取得方法は別途Gitなどから取得する必要あり
        # 今は指示からの出力（仮にdiff形式とする）をReviewerに渡す
        dummy_diff = f"diff --git a/fake_file.py b/fake_file.py\n{programmer_output}"

        # Step 2: レビュー実施
        reviewer_input = ReviewerInput(
            diff=dummy_diff,
            programmer_comment=reviewer_comment or "最初のコードレビューです。",
        )
        reviewer_output = reviewer_agent.run(reviewer_input)

        # 出力表示
        print(f"\n🧑‍⚖️ Reviewer Summary:\n{reviewer_output.summary}")
        print(f"\n👍 LGTM: {reviewer_output.lgtm}")

        if reviewer_output.lgtm:
            print("\n✅ レビュー完了！LGTM獲得。開発終了。\n")
            break
        else:
            reviewer_comment = reviewer_output.summary
    else:
        print("\n⚠️ 最大リトライ回数に達しました。LGTMを獲得できませんでした。")


if __name__ == "__main__":
    main()
