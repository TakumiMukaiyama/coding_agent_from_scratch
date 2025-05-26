from src.usecase.programmer.agent import ProgrammerAgent


def main():
    agent = ProgrammerAgent()

    # ここがテストプロンプト
    instruction = """
    src/reviewer_agent/functionディレクトリ配下に新しくファイルを作成してください。
    ファイル名はfunction_test.pyとします。
    ファイルの内容は、以下のようにしてください。
    
    def test_function():
        assert True
    """

    try:
        result = agent.run(instruction)
        print("Agent実行成功!")
        print("出力内容:")
        print(result)
    except Exception as e:
        print("Agent実行中にエラーが発生しました:")
        print(str(e))


if __name__ == "__main__":
    main()
