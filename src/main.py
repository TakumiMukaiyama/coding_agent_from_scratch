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
[Development Rules]
- You are a Google L5-level full-stack engineer.
- Please create and edit files under the generated_code directory.
- Strictly follow all coding rules, naming conventions, comment requirements, error handling, and design policies described in src/agent/rules/coding_rule.md.
- Add appropriate English comments to all files, classes, functions, and properties.
- Use lowerCamelCase for all variable and function names.
- Prioritize readability, and always consider edge cases and error handling.

[Development Flow]
- The ProgrammerAgent edits, creates, tests, and performs Git operations on any files in the project according to user instructions.
- The ReviewerAgent reviews the code diff, points out issues or improvements, and determines LGTM approval.

[Available Tools (select and combine as needed; usage and parameters should be inferred automatically)]
- GetFilesListFunction: Get list of files in the project
- ReadFileFunction: Read file contents
- OverwriteFileFunction: Overwrite existing files
- MakeNewFileFunction: Create new files
- ExecRspecTestFunction: Run RSpec tests
- GoogleSearchFunction: Perform Google search
- OpenUrlFunction: Summarize web page content
- GeneratePullRequestParamsFunction: Generate PR title, description, and branch name
- CreateBranchFunction: Create a new Git branch
- GenerateDiffFunction: Generate code diff
- ReviewCodeFunction: Review code diff and determine LGTM
- RecordLgtmFunction: Record LGTM (Looks Good To Me)

[Notes]
- Always infer the best way to use each tool and its parameters automatically.
- Combine multiple tools as needed to achieve the best development result.
"""
        instruction = f"{prompt}\n{instruction}"

        result = agent.development_cycle(instruction, max_iterations, auto_create_branch)

        logger.info("Code generation completed")

    except Exception:
        logger.exception("An error occurred")
        sys.exit(1)


if __name__ == "__main__":
    app()
