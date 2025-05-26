import subprocess

from src.agent.schema.create_branch_input import CreateBranchInput
from src.application.function.base import BaseFunction
from langchain_core.tools import StructuredTool


class CreateBranchFunction(BaseFunction):
    """新しいGitブランチを作成するFunction"""

    @staticmethod
    def execute(branch_name: str) -> dict[str, str]:
        """新しいGitブランチを作成する

        Args:
            branch_name (str): 作成するブランチ名

        Returns:
            Dict[str, str]: 実行結果
        """
        try:
            # 現在のブランチを取得
            current_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.STDOUT,
                text=True,
            ).strip()

            # すでにそのブランチが存在するか確認
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
                # すでに存在する場合はチェックアウト
                subprocess.check_output(
                    ["git", "checkout", branch_name],
                    stderr=subprocess.STDOUT,
                )
                return {
                    "result": "success",
                    "message": f"既存のブランチ '{branch_name}' に切り替えました",
                    "current_branch": branch_name,
                    "previous_branch": current_branch,
                }

            # 新しいブランチを作成
            subprocess.check_output(
                ["git", "checkout", "-b", branch_name],
                stderr=subprocess.STDOUT,
            )

            return {
                "result": "success",
                "message": f"新しいブランチ '{branch_name}' を作成しました",
                "current_branch": branch_name,
                "previous_branch": current_branch,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"ブランチ作成に失敗しました: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["CreateBranchFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="新しいGitブランチを作成します。既に存在する場合はそのブランチに切り替えます。",
            func=cls.execute,
            args_schema=CreateBranchInput,
        )
