import subprocess

from langchain_core.tools import StructuredTool

from src.agent.schema.generate_diff_input import GenerateDiffInput
from src.application.function.base import BaseFunction


class GenerateDiffFunction(BaseFunction):
    """Gitのdiffを生成するFunction."""

    @staticmethod
    def execute(
        base_branch: str | None = None,
        target_branch: str | None = None,
        file_path: str | None = None,
    ) -> dict[str, str]:
        """Gitのdiffを生成する.

        Args:
            base_branch (str, optional): ベースとなるブランチ名. デフォルトは "main"
            target_branch (Optional[str], optional): 比較対象のブランチ名. デフォルトはNone（現在のブランチ）
            file_path (Optional[str], optional): 特定のファイルパス. デフォルトはNone（全ファイル）

        Returns:
            Dict[str, str]: 実行結果
        """
        try:
            # デフォルト値の設定
            if base_branch is None:
                base_branch = "main"

            # 現在のブランチを取得
            if target_branch is None:
                target_branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

            # diffコマンド構築
            cmd = ["git", "diff"]

            # ベースブランチとターゲットブランチが同じ場合は、ワーキングディレクトリとの差分を取得
            if base_branch == target_branch:
                # ワーキングディレクトリの変更を取得
                pass  # git diffのみ
            else:
                # ブランチ間の差分を取得
                cmd.append(f"{base_branch}...{target_branch}")

            # 特定のファイルのdiffを取得する場合
            if file_path:
                cmd.append("--")
                cmd.append(file_path)

            # diffを実行
            diff_output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # 結果がない場合
            if not diff_output:
                return {
                    "result": "success",
                    "message": "差分はありません",
                    "diff": "",
                    "base_branch": base_branch,
                    "target_branch": target_branch,
                }
            return {
                "result": "success",
                "message": f"{base_branch}と{target_branch}の差分を取得しました",
                "diff": diff_output,
                "base_branch": base_branch,
                "target_branch": target_branch,
            }

        except subprocess.CalledProcessError as e:
            return {
                "result": "error",
                "message": f"diff取得に失敗しました: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["GenerateDiffFunction"]) -> StructuredTool:
        """ツールを作成する."""
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Gitリポジトリの差分（diff）を取得します。ブランチ間やファイル単位での差分を取得できます。",
            func=cls.execute,
            args_schema=GenerateDiffInput,
        )
