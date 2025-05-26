import subprocess

from langchain_core.tools import StructuredTool

from src.agent.schema.generate_diff_input import GenerateDiffInput
from src.application.function.base import BaseFunction


class GenerateDiffFunction(BaseFunction):
    """Function to generate Git diff."""

    @staticmethod
    def execute(
        base_branch: str | None = None,
        target_branch: str | None = None,
        file_path: str | None = None,
    ) -> dict[str, str]:
        """Generate local Git diff.

        Check differences in the following order:
        1. Working directory changes (git diff HEAD)
        2. Staging area changes (git diff --cached)
        3. Untracked files (git ls-files --others --exclude-standard)

        Args:
            base_branch (str, optional): Not used (kept for compatibility)
            target_branch (Optional[str], optional): Not used (kept for compatibility)
            file_path (Optional[str], optional): Specific file path. Defaults to None (all files)

        Returns:
            Dict[str, str]: Execution result
        """
        try:
            # Set default values
            if base_branch is None:
                base_branch = "main"

            # Get current branch
            if target_branch is None:
                target_branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

            # Build diff command - get local changes
            cmd = ["git", "diff"]

            # Get diff between HEAD and working directory (local changes)
            cmd.append("HEAD")

            # Get diff for specific file if specified
            if file_path:
                cmd.append("--")
                cmd.append(file_path)

            # Execute working directory diff
            diff_output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # If no changes in working directory, also check staging area changes
            if not diff_output:
                # Get diff between staging area (index) and HEAD
                cmd_staged = ["git", "diff", "--cached"]
                if file_path:
                    cmd_staged.extend(["--", file_path])

                staged_output = subprocess.check_output(
                    cmd_staged,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                diff_output = staged_output

            # Also check untracked files
            if not diff_output:
                # Get list of untracked files
                untracked_cmd = ["git", "ls-files", "--others", "--exclude-standard"]
                if file_path:
                    untracked_cmd.append(file_path)

                untracked_files = subprocess.check_output(
                    untracked_cmd,
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

                if untracked_files:
                    # Display untracked file contents in diff format
                    untracked_diff = ""
                    for file in untracked_files.split("\n"):
                        if file.strip():
                            try:
                                # Read file content and display in diff format
                                with open(file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                untracked_diff += f"diff --git a/{file} b/{file}\n"
                                untracked_diff += "new file mode 100644\n"
                                untracked_diff += (
                                    f"index 0000000..{hash(content) % 1000000:07x}\n"
                                )
                                untracked_diff += "--- /dev/null\n"
                                untracked_diff += f"+++ b/{file}\n"
                                for i, line in enumerate(content.split("\n"), 1):
                                    untracked_diff += f"+{line}\n"
                                untracked_diff += "\n"
                            except (UnicodeDecodeError, FileNotFoundError):
                                # Skip binary files or unreadable files
                                untracked_diff += f"diff --git a/{file} b/{file}\n"
                                untracked_diff += "new file mode 100644\n"
                                untracked_diff += f"Binary file {file} added\n\n"

                    diff_output = untracked_diff

            # If no results
            if not diff_output:
                return {
                    "result": "success",
                    "message": "No local diff found",
                    "diff": "",
                    "base_branch": base_branch,
                    "target_branch": target_branch,
                }
            # Determine diff type and set message
            if "new file mode" in diff_output:
                message = "Local diff retrieved (including untracked files)"
            else:
                message = "Local diff retrieved"

            return {
                "result": "success",
                "message": message,
                "diff": diff_output,
                "base_branch": base_branch,
                "target_branch": target_branch,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"Failed to retrieve diff: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["GenerateDiffFunction"]) -> StructuredTool:
        """Create tool."""
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Retrieve local diff from Git repository. Can retrieve changes including working directory, staging area, and untracked files.",
            func=cls.execute,
            args_schema=GenerateDiffInput,
        )
