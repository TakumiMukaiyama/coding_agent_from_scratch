import subprocess

from langchain_core.tools import StructuredTool

from src.agent.schema.git_commit_push_input import GitCommitPushInput
from src.application.function.base import BaseFunction


class GitCommitPushFunction(BaseFunction):
    """Function to commit and push changes"""

    @staticmethod
    def execute(
        path_to_add: str = ".",
        commit_message: str = "",
        remote_name: str = "origin",
        branch_name: str = "",
        force_push: bool = False,
    ) -> dict[str, str]:
        """Stage changes, commit them, and push to remote repository

        Args:
            path_to_add (str, optional): Path to add. Default is "." (all changes).
            commit_message (str, optional): Commit message. Default is empty string.
            remote_name (str, optional): Remote name. Default is "origin".
            branch_name (str, optional): Target branch name for push. If empty, uses current branch.
            force_push (bool, optional): Whether to force push. Default is False.

        Returns:
            Dict[str, str]: Execution result
        """
        try:
            # Get current branch (used when branch_name is empty)
            if not branch_name:
                branch_name = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

            # Add changes to staging
            add_result = subprocess.check_output(
                ["git", "add", path_to_add],
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Set default message if commit message is empty
            if not commit_message:
                commit_message = f"Update files in {path_to_add}"

            # Commit changes
            commit_result = subprocess.check_output(
                ["git", "commit", "-m", commit_message],
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Push to remote repository
            push_command = ["git", "push"]
            if force_push:
                push_command.append("--force")
            push_command.extend([remote_name, branch_name])

            push_result = subprocess.check_output(
                push_command,
                stderr=subprocess.STDOUT,
                text=True,
            )

            return {
                "result": "success",
                "message": "Changes committed and pushed successfully",
                "add_result": add_result,
                "commit_result": commit_result,
                "push_result": push_result,
                "branch": branch_name,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"Failed to commit or push: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["GitCommitPushFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Stage changes, commit them, and push to remote repository.",
            func=cls.execute,
            args_schema=GitCommitPushInput,
        )
