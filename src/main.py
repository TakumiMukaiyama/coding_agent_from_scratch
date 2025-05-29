import sys

import typer
from dotenv import load_dotenv

from src.infrastructure.utils.logger import get_logger
from src.usecase.agent_coordinator import AgentCoordinator

load_dotenv()

logger = get_logger(__name__)

app = typer.Typer(help="Agent execution CLI")


@app.command()
def coordinator(
    instruction: str = typer.Argument(..., help="Instruction content for programmer agent"),
):
    """Execute Programmer agent."""
    try:
        agent = AgentCoordinator()
        max_iterations = 3
        auto_create_branch = True
        prompt = """
        Please create and edit files under the generated_code directory.
        Refer to and strictly follow the code generation rules in src/agent/rules/coding_rule.md.
        ※ Execution confirmation is not required. Please edit the files.
        
        【Programmerが利用可能なTool】
        - GetFilesListFunction: プロジェクト配下のファイル一覧を取得します。例: すべてのファイル, Pythonファイルのみ, 特定パターン, 除外パターン, 特定ディレクトリなど柔軟に指定可能です。
        - ReadFileFunction: 指定ファイルの内容を取得します。
        - OverwriteFileFunction: 指定ファイルを新しい内容で上書きします。
        - MakeNewFileFunction: 新しいファイルを作成します。
        - ExecRspecTestFunction: RSpecテストを実行します。
        - GoogleSearchFunction: Google検索を行い結果を返します。
        - OpenUrlFunction: URLのページ内容を要約して返します。
        - GeneratePullRequestParamsFunction: PRのタイトル・説明・ブランチ名を生成します。
        - CreateBranchFunction: 新しいGitブランチを作成します。
        - GenerateDiffFunction: 変更内容のdiffを生成します。
        
        【Reviewerが利用可能なTool】
        - ReviewCodeFunction: プルリクエストのコード差分をレビューし、問題点や改善点を要約し、LGTM可否を判定します。
        - RecordLgtmFunction: 現在の作業内容をLGTM（Looks Good To Me）として記録します。
        
        各Toolの詳細な使い方やパラメータは、必要に応じて自動的に推論してください。
        """
        instruction = f"{prompt}\n{instruction}"

        result = agent.development_cycle(instruction, max_iterations, auto_create_branch)

        logger.info("Code generation completed")

    except Exception:
        logger.exception("An error occurred")
        sys.exit(1)


if __name__ == "__main__":
    app()
