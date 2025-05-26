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
    instruction: str = typer.Argument(
        ..., help="Instruction content for programmer agent"
    ),
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
        """
        instruction = f"{prompt}\n{instruction}"

        result = agent.development_cycle(
            instruction, max_iterations, auto_create_branch
        )

        logger.info("Code generation completed")

    except Exception:
        logger.exception("An error occurred")
        sys.exit(1)


if __name__ == "__main__":
    app()
