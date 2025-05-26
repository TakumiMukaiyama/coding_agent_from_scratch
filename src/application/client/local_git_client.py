import os
import sys
from git import Repo
from github import GithubException
from src.application.client.github_client import GitHubClient
from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class GitCommitPushPR:
    """エージェントが編集したファイルをコミット、プッシュし、PRを作成するクラス."""

    def __init__(self, repo_path: str, github_token: str, repo_full_name: str, github_username: str):
        """初期化.

        Args:
            repo_path: ローカルリポジトリのパス
            github_token: GitHubアクセストークン
            repo_full_name: 'ユーザー名/リポジトリ名'形式のリポジトリ名
        """
        self.repo_path = repo_path
        self.repo_full_name = repo_full_name
        self.github_token = github_token
        self.github_username = github_username
        self.repo = Repo(repo_path)
        self.github_client = GitHubClient(github_token)

    def commit_changes(self, file_paths: list[str], commit_message: str) -> dict:
        """変更をコミットする."""
        try:
            self.repo.git.add(file_paths)
            commit = self.repo.index.commit(commit_message)
            logger.info(f"変更をコミットしました: {commit.hexsha}")
            return {
                "commit": {"sha": commit.hexsha, "message": commit_message},
                "files": file_paths,
            }
        except Exception:
            logger.exception()
            raise

    def push_to_remote(self, branch_name: str | None = None) -> bool:
        """リモートリポジトリに変更をプッシュする（PATを用いたHTTPS認証）."""
        try:
            if branch_name is None:
                branch_name = self.repo.active_branch.name

            if "origin" not in [remote.name for remote in self.repo.remotes]:
                raise ValueError("リモート 'origin' が設定されていません")

            # 認証情報付きURLに置換
            remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.repo_full_name}.git"

            origin = self.repo.remote("origin")
            origin.set_url(remote_url)

            # Push実行
            self.repo.git.push("--set-upstream", "origin", branch_name)
            logger.info(f"変更をリモートにプッシュしました: {branch_name}")
            return True
        except Exception:
            logger.exception()
            raise

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str | None = None,
        base_branch: str = "main",
    ) -> dict:
        """プルリクエストを作成する."""
        try:
            if head_branch is None:
                head_branch = self.repo.active_branch.name

            if head_branch == base_branch:
                raise ValueError(f"ベースブランチ '{base_branch}' とヘッドブランチ '{head_branch}' が同じです")

            pr = self.github_client.create_pull_request(
                repo_full_name=self.repo_full_name,
                title=title,
                body=body,
                head_branch=head_branch,
                base_branch=base_branch,
            )

            logger.info(f"PRを作成しました: #{pr.number} - {pr.html_url}")
            return {"number": pr.number, "title": pr.title, "url": pr.html_url}

        except GithubException as e:
            error_message = str(e)
            if hasattr(e, "data") and isinstance(e.data, dict):
                msg = e.data.get("message", "")
                errors = e.data.get("errors", [])
                details = ", ".join([err.get("message", str(err)) for err in errors])
                error_message = f"{msg} - {details}" if details else msg

            logger.exception(f"PRの作成に失敗しました: {error_message}")
            raise GithubException(e.status, error_message)
        except Exception:
            logger.exception()
            raise
