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

    except Exception:
        logger.exception("エラーが発生しました")
        sys.exit(1)


if __name__ == "__main__":
    app()
