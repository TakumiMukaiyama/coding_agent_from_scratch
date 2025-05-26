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
        """ローカルのGit差分を生成する.

        以下の順序で差分を確認します：
        1. ワーキングディレクトリの変更（git diff HEAD）
        2. ステージングエリアの変更（git diff --cached）
        3. 未追跡ファイル（git ls-files --others --exclude-standard）

        Args:
            base_branch (str, optional): 使用されません（互換性のため保持）
            target_branch (Optional[str], optional): 使用されません（互換性のため保持）
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

            # diffコマンド構築 - ローカルの変更を取得
            cmd = ["git", "diff"]

            # HEADとワーキングディレクトリの差分を取得（ローカルの変更）
            cmd.append("HEAD")

            # 特定のファイルのdiffを取得する場合
            if file_path:
                cmd.append("--")
                cmd.append(file_path)

                # ワーキングディレクトリの差分を実行
            diff_output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # ワーキングディレクトリに変更がない場合、ステージングエリアの変更も確認
            if not diff_output:
                # ステージングエリア（インデックス）とHEADの差分を取得
                cmd_staged = ["git", "diff", "--cached"]
                if file_path:
                    cmd_staged.extend(["--", file_path])

                staged_output = subprocess.check_output(
                    cmd_staged,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                diff_output = staged_output

            # 追跡されていないファイルも確認
            if not diff_output:
                # 未追跡ファイルの一覧を取得
                untracked_cmd = ["git", "ls-files", "--others", "--exclude-standard"]
                if file_path:
                    untracked_cmd.append(file_path)

                untracked_files = subprocess.check_output(
                    untracked_cmd,
                    stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

                if untracked_files:
                    # 未追跡ファイルの内容を差分形式で表示
                    untracked_diff = ""
                    for file in untracked_files.split("\n"):
                        if file.strip():
                            try:
                                # ファイルの内容を読み取り、diff形式で表示
                                with open(file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                untracked_diff += f"diff --git a/{file} b/{file}\n"
                                untracked_diff += "new file mode 100644\n"
                                untracked_diff += f"index 0000000..{hash(content) % 1000000:07x}\n"
                                untracked_diff += "--- /dev/null\n"
                                untracked_diff += f"+++ b/{file}\n"
                                for i, line in enumerate(content.split("\n"), 1):
                                    untracked_diff += f"+{line}\n"
                                untracked_diff += "\n"
                            except (UnicodeDecodeError, FileNotFoundError):
                                # バイナリファイルや読み取れないファイルはスキップ
                                untracked_diff += f"diff --git a/{file} b/{file}\n"
                                untracked_diff += "new file mode 100644\n"
                                untracked_diff += f"Binary file {file} added\n\n"

                    diff_output = untracked_diff

            # 結果がない場合
            if not diff_output:
                return {
                    "result": "success",
                    "message": "ローカルに差分はありません",
                    "diff": "",
                    "base_branch": base_branch,
                    "target_branch": target_branch,
                }
            # 差分の種類を判定してメッセージを設定
            if "new file mode" in diff_output:
                message = "ローカルの差分を取得しました（未追跡ファイルを含む）"
            else:
                message = "ローカルの差分を取得しました"

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
                "message": f"diff取得に失敗しました: {str(e)}",
                "error": e.output,
            }

    @classmethod
    def to_tool(cls: type["GenerateDiffFunction"]) -> StructuredTool:
        """ツールを作成する."""
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Gitリポジトリのローカル差分（diff）を取得します。ワーキングディレクトリ、ステージングエリア、未追跡ファイルの変更を含めて取得できます。",
            func=cls.execute,
            args_schema=GenerateDiffInput,
        )
