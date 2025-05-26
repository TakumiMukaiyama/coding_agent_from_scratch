import os
import subprocess

from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate

from src.agent.function.generate_pr_params import GeneratePullRequestParamsFunction
from src.agent.schema.reviewer_input import ReviewerInput
from src.agent.schema.reviewer_output import ReviewerOutput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.infrastructure.utils.logger import get_logger
from src.usecase.programmer.agent import ProgrammerAgent
from src.usecase.reviewer.agent import ReviewerAgent

logger = get_logger(__name__)


class AgentCoordinator:
    """ProgrammerAgentとReviewerAgentの連携を行うコーディネーター."""

    def __init__(self):
        """コンストラクタ."""
        self.programmer_agent = ProgrammerAgent()
        self.reviewer_agent = ReviewerAgent()
        self.base_branch = "main"
        self.working_branch = None
        self.llm_client = AzureOpenAIClient()
        self.chat_llm = self.llm_client.initialize_chat()
        self.repo_path = os.getcwd()  # カレントディレクトリをリポジトリパスとして使用
        self.repo_full_name = "coding_agent_from_scratch"

    def generate_branch_name(self, instruction: str) -> str:
        """指示内容からGitブランチ名を生成します.

        Args:
            instruction (str): プログラマーへの指示

        Returns:
            str: 生成されたブランチ名
        """
        prompt = PromptTemplate.from_template(
            """
あなたはGitのブランチ命名の専門家です。
以下の指示内容から、適切なGitブランチ名を生成してください。

ブランチ名のルール:
1. 'feature/', 'bugfix/', 'refactor/' などの適切なプレフィックスを使用する
2. 英語の小文字、数字、ハイフン(-)のみを使用する（スペースや特殊文字は使用しない）
3. 簡潔で、内容を表す名前にする
4. 単語の区切りにはハイフンを使用する
5. 最大50文字以内にする

指示内容:
{instruction}

出力する形式:
ブランチ名のみを出力してください。説明や前後のテキストは不要です。
            """,
        )

        message = [HumanMessage(content=prompt.format(instruction=instruction))]
        result = self.chat_llm.invoke(message)

        # 余分な空白や改行を削除して整形
        branch_name = result.content.strip()

        return branch_name

    def create_working_branch(self, branch_name: str) -> str:
        """作業用ブランチを作成します.

        Args:
            branch_name (str): 作成するブランチ名

        Returns:
            str: 作成・切替結果のメッセージ
        """
        from src.agent.function.create_branch import CreateBranchFunction

        branch_function = CreateBranchFunction()
        result = branch_function.execute(branch_name=branch_name)

        if result["result"] == "success":
            self.working_branch = branch_name

        return result["message"]

    def run_programmer(self, instruction: str, reviewer_comment: str = None) -> str:
        """プログラマーエージェントを実行します.

        Args:
            instruction (str): プログラマーへの指示
            reviewer_comment (str, optional): レビュアーからのコメント. デフォルトは None.

        Returns:
            str: プログラマーの出力
        """
        return self.programmer_agent.run(instruction, reviewer_comment)

    def run_reviewer(self, programmer_comment: str = None) -> ReviewerOutput:
        """レビュアーエージェントを実行します.

        Args:
            programmer_comment (str, optional): プログラマーからのコメント. デフォルトは None.

        Returns:
            ReviewerOutput: レビュー結果
        """
        if not self.working_branch:
            error_msg = "作業用ブランチが設定されていません。create_working_branch()を先に実行してください."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 現在の差分を取得
        diff = self.programmer_agent.get_diff(
            file_path=self.repo_path,
        )
        logger.info(f"diff: {diff}")

        # レビュアーエージェントを実行
        reviewer_input = ReviewerInput(
            diff=diff,
            programmer_comment=programmer_comment,
        )

        return self.reviewer_agent.run(reviewer_input)

    def development_cycle(
        self,
        instruction: str,
        max_iterations: int = 3,
        auto_create_branch: bool = True,
    ) -> dict:
        """プログラマーとレビュアーのサイクルを実行します.

        Args:
            instruction (str): プログラマーへの初期指示
            max_iterations (int, optional): 最大反復回数. デフォルトは 3.
            auto_create_branch (bool, optional): 自動的にブランチを生成・作成するかどうか. デフォルトは True.

        Returns:
            dict: 開発サイクルの実行結果

        Raises:
            ValueError: 作業用ブランチが設定されていない、または差分がない場合
        """
        programmer_output = None
        reviewer_output = None

        try:
            # 作業用ブランチの自動生成・作成
            if auto_create_branch and not self.working_branch:
                self.working_branch = self.generate_branch_name(instruction)
                logger.info(f"ブランチ名を生成しました: {self.working_branch}")

            if not self.working_branch:
                raise ValueError(
                    "ブランチ名が設定されていません。create_working_branch()を先に実行するか、auto_create_branch=Trueを指定してください。"
                )

            # 開発サイクルの実行
            for i in range(max_iterations):
                logger.info(f"=== 開発サイクル {i + 1}/{max_iterations} ===")

                programmer_output = self.run_programmer(
                    instruction,
                    reviewer_comment=reviewer_output.summary if reviewer_output else None,
                )
                logger.info(f"プログラマー出力: {programmer_output[:100]}...")

                reviewer_output = self.run_reviewer(
                    programmer_comment=f"開発サイクル {i + 1} の実装が完了しました。差分がない場合LGTMしないでください。"
                )
                logger.info(f"レビュアー出力: {reviewer_output.summary[:100]}...")

                if reviewer_output.lgtm:
                    logger.info("レビュー承認 (LGTM) が得られました。サイクルを終了します。")
                    break

            # 差分の確認と処理
            diff = self.programmer_agent.get_diff(file_path=self.repo_path)
            if not diff:
                raise ValueError("差分がありません。プルリクエストを作成できません。")

            try:
                diff_output = subprocess.check_output(
                    [
                        "git",
                        "diff",
                        "--name-only",
                        "HEAD",
                        "--",
                        self.repo_path,
                    ],
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"git diffコマンドの実行に失敗しました: {e}")
                raise

            # PRの作成
            pr_params = GeneratePullRequestParamsFunction.execute(
                instruction=instruction,
                programmer_output=programmer_output,
                diff=diff,
            )

            return {
                "programmer_output": programmer_output,
                "reviewer_output": reviewer_output.summary if reviewer_output else None,
                "branch_name": self.working_branch,
                "pr_title": pr_params["pr_title"],
                "pr_description": pr_params["pr_description"],
            }

        except Exception as e:
            logger.exception(f"開発サイクルの実行中にエラーが発生しました: {e}")
            raise
