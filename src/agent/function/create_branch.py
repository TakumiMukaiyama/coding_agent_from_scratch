import subprocess

from langchain_core.tools import StructuredTool

from src.agent.schema.create_branch_input import CreateBranchInput
from src.application.function.base import BaseFunction


class CreateBranchFunction(BaseFunction):
    """Function to create a new Git branch"""

    @staticmethod
    def execute(branch_name: str) -> dict[str, str]:
        """Create a new Git branch

        Args:
            branch_name (str): Name of the branch to create

        Returns:
            Dict[str, str]: Execution result
        """
        try:
            # Get current branch
            current_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.STDOUT,
                text=True,
            ).strip()

            # Check if the branch already exists
            all_branches_output = subprocess.check_output(
                ["git", "branch"],
                stderr=subprocess.STDOUT,
                text=True,
            )
            branch_list = [
                line.strip().lstrip("* ").strip()
                for line in all_branches_output.splitlines()
            ]

            if branch_name in branch_list:
                # If it already exists, checkout to it
                subprocess.check_output(
                    ["git", "checkout", branch_name],
                    stderr=subprocess.STDOUT,
                )
                return {
                    "result": "success",
                    "message": f"Switched to existing branch '{branch_name}'",
                    "current_branch": branch_name,
                    "previous_branch": current_branch,
                }

            # Create new branch
            subprocess.check_output(
                ["git", "checkout", "-b", branch_name],
                stderr=subprocess.STDOUT,
            )

            return {
                "result": "success",
                "message": f"Created new branch '{branch_name}'",
                "current_branch": branch_name,
                "previous_branch": current_branch,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"Failed to create branch: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["CreateBranchFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Creates a new Git branch. If it already exists, switches to that branch.",
            func=cls.execute,
            args_schema=CreateBranchInput,
        )
