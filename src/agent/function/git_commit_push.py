import subprocess

from src.agent.schema.git_commit_push_input import GitCommitPushInput
from src.application.function.base import BaseFunction
from langchain_core.tools import StructuredTool


class GitCommitPushFunction(BaseFunction):
    """変更をコミットしてプッシュするFunction"""

    @staticmethod
    def execute(
        path_to_add: str = ".",
        commit_message: str = "",
        remote_name: str = "origin",
        branch_name: str = "",
        force_push: bool = False,
    ) -> dict[str, str]:
        """変更をステージングしてコミットし、リモートリポジトリにプッシュする

        Args:
            path_to_add (str, optional): addするパス. デフォルトは "." (すべての変更).
            commit_message (str, optional): コミットメッセージ. デフォルトは空文字.
            remote_name (str, optional): リモート名. デフォルトは "origin".
            branch_name (str, optional): プッシュ先のブランチ名. 空の場合は現在のブランチ.
            force_push (bool, optional): 強制プッシュするかどうか. デフォルトはFalse.

        Returns:
            Dict[str, str]: 実行結果
        """
        try:
            # 現在のブランチを取得（branch_nameが空の場合に使用）
            if not branch_name:
                branch_name = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

            # 変更をステージングに追加
            add_result = subprocess.check_output(
                ["git", "add", path_to_add],
                stderr=subprocess.STDOUT,
                text=True,
            )

            # コミットメッセージが空の場合はデフォルトメッセージを設定
            if not commit_message:
                commit_message = f"Update files in {path_to_add}"

            # 変更をコミット
            commit_result = subprocess.check_output(
                ["git", "commit", "-m", commit_message],
                stderr=subprocess.STDOUT,
                text=True,
            )

            # リモートリポジトリにプッシュ
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
                "message": "変更をコミットしてプッシュしました",
                "add_result": add_result,
                "commit_result": commit_result,
                "push_result": push_result,
                "branch": branch_name,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"コミットまたはプッシュに失敗しました: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["GitCommitPushFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="変更をステージングしてコミットし、リモートリポジトリにプッシュします。",
            func=cls.execute,
            args_schema=GitCommitPushInput,
        ) 