import sys

import typer
from dotenv import load_dotenv

from src.infrastructure.utils.logger import get_logger
from src.usecase.agent_coordinator import AgentCoordinator

load_dotenv()

logger = get_logger(__name__)

app = typer.Typer(help="エージェント実行CLI")


@app.command()
def coordinator(
    instruction: str = typer.Argument(..., help="プログラマーエージェントへの指示内容"),
):
    """Programmerエージェントを実行します."""
    try:
        agent = AgentCoordinator()
        max_iterations = 3
        auto_create_branch = True
        prompt = """
        generated_codeディレクトリ配下でファイルの作成、編集を行なってください。
        コードの生成ルールは src/agent/rules/coding_rule.md を参照し、厳守してください。
        ※ 実行確認は不要です。ファイルの編集を行なってください
        """
        instruction = f"{prompt}\n{instruction}"

        result = agent.development_cycle(instruction, max_iterations, auto_create_branch)

        logger.info("コードの生成が完了しました")

        # ブランチの変更を確認
        branch_name = result.get("branch_name", "")
        if not branch_name:
            logger.warning("作業ブランチ名が設定されていません。")
            sys.exit(1)

        # PR情報の取得
        pr_number = result.get("pr_number")
        pr_url = result.get("pr_url")

        if not pr_number:
            logger.error("プルリクエストの作成に失敗しました")
            sys.exit(1)

        logger.info(f"プルリクエストが作成されました: PR #{pr_number}")
        if pr_url:
            logger.info(f"PR URL: {pr_url}")

    except Exception:
        logger.exception("エラーが発生しました")
        sys.exit(1)


if __name__ == "__main__":
    app()
