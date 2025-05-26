"""GitHubリポジトリとの対話を行うためのクライアントクラス。
PyGithubライブラリを使用してGitHub APIと通信します。
"""

import base64
import os
import sys
from typing import Any

from github import Github, GithubException, InputGitTreeElement
from github.Branch import Branch
from github.ContentFile import ContentFile
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository


class GitHubClient:
    """GitHub APIと対話するためのクライアントクラス.

    認証、リポジトリ操作、ファイル操作、ブランチ操作、PRやイシューの作成などの
    一般的なGitHub操作を提供します.
    """

    def __init__(self, access_token: str | None = None):
        """GitHub APIクライアントを初期化.

        Args:
            access_token: GitHub個人アクセストークン（オプション）.
                          指定がない場合は環境変数GITHUB_TOKENから取得します.
        """
        if access_token is None:
            access_token = os.environ.get("GITHUB_TOKEN")
            if not access_token:
                print(
                    "環境変数GITHUB_TOKENが設定されていません。GitHubの操作ができません。"
                )
                sys.exit(1)

        self.github = Github(access_token)

    def get_repository(self, repo_full_name: str) -> Repository:
        """指定された名前のリポジトリを取得.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
        Returns:
            Repository: 取得したリポジトリオブジェクト
        Raises:
            GithubException: リポジトリが見つからない、またはアクセス権がない場合
        """
        try:
            return self.github.get_repo(repo_full_name)
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"リポジトリ '{repo_full_name}' の取得に失敗しました: {error_message}",
            )

    def get_file_content(
        self, repo_full_name: str, file_path: str, ref: str | None = None
    ) -> str:
        """リポジトリ内の指定されたファイルの内容を取得.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            file_path: 取得するファイルのパス
            ref: 取得するブランチまたはコミットのリファレンス（デフォルト: リポジトリのデフォルトブランチ）
        Returns:
            str: ファイルの内容
        Raises:
            GithubException: ファイルが見つからないか、アクセスできない場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            content_file = repo.get_contents(file_path, ref=ref)

            if isinstance(content_file, list):
                raise ValueError(
                    f"'{file_path}' はディレクトリです。ファイルパスを指定してください。"
                )

            # ファイル内容をデコード
            content = base64.b64decode(content_file.content).decode("utf-8")
            return content
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"ファイル '{file_path}' の取得に失敗しました: {error_message}",
            )

    def create_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """リポジトリに新しいファイルを作成.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            file_path: 作成するファイルのパス
            content: ファイルの内容
            commit_message: コミットメッセージ
            branch: ファイルを作成するブランチ名（デフォルト: リポジトリのデフォルトブランチ）

        Returns:
            Dict: 作成結果の情報を含む辞書

        Raises:
            GithubException: ファイル作成に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content.encode("utf-8"),
                branch=branch,
            )
            return result
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"ファイル '{file_path}' の作成に失敗しました: {error_message}",
            )

    def update_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        branch: str,
        commit_message: str = "agent-update",
    ) -> dict[str, Any]:
        """リポジトリ内の既存ファイルを更新.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            file_path: 更新するファイルのパス
            content: 新しいファイル内容
            commit_message: コミットメッセージ
            branch: ファイルを更新するブランチ名（デフォルト: リポジトリのデフォルトブランチ）

        Returns:
            Dict: 更新結果の情報を含む辞書

        Raises:
            GithubException: ファイル更新に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            sha = self.get_file_sha(repo_full_name, file_path, branch)
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content.encode("utf-8"),
                sha=sha,
                branch=branch,
            )
            return result
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"ファイル '{file_path}' の更新に失敗しました: {error_message}",
            )

    def get_file_sha(
        self, repo_full_name: str, file_path: str, ref: str | None = None
    ) -> str:
        """ファイルのSHA値を取得.

        ファイル更新時に必要です.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            file_path: ファイルのパス
            ref: 取得するブランチまたはコミットのリファレンス（デフォルト: リポジトリのデフォルトブランチ）

        Returns:
            str: ファイルのSHA値

        Raises:
            GithubException: ファイルが見つからないか、アクセスできない場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            content_file = repo.get_contents(file_path, ref=ref)

            if isinstance(content_file, list):
                raise ValueError(
                    f"'{file_path}' はディレクトリです。ファイルパスを指定してください。"
                )

            return content_file.sha
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"ファイル '{file_path}' のSHA取得に失敗しました: {error_message}",
            )

    def create_branch(
        self, repo_full_name: str, new_branch_name: str, base_branch: str | None = None
    ) -> Branch:
        """既存のブランチを基にして新しいブランチを作成.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            new_branch_name: 作成する新しいブランチの名前
            base_branch: 基にするブランチ名（デフォルト: リポジトリのデフォルトブランチ）

        Returns:
            Branch: 作成されたブランチオブジェクト

        Raises:
            GithubException: ブランチ作成に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)

            # ベースブランチが指定されていない場合はデフォルトブランチを使用
            if base_branch is None:
                base_branch = repo.default_branch

            # ベースブランチのリファレンスを取得
            base_branch_ref = repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_branch_ref.object.sha

            # 新しいブランチを作成
            repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_sha)

            # 作成したブランチを返す
            return repo.get_branch(new_branch_name)
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"ブランチ '{new_branch_name}' の作成に失敗しました: {error_message}",
            )

    def list_branches(self, repo_full_name: str) -> list[str]:
        """リポジトリのブランチ一覧を取得.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名

        Returns:
            List[str]: ブランチ名のリスト

        Raises:
            GithubException: ブランチ一覧の取得に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            branches = list(repo.get_branches())
            return [branch.name for branch in branches]
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"ブランチの一覧取得に失敗しました: {error_message}"
            )

    def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        draft: bool = False,
    ) -> PullRequest:
        """リポジトリにプルリクエストを作成.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            title: PRのタイトル
            body: PRの説明
            head_branch: 変更を含むブランチ
            base_branch: マージ先のブランチ
            draft: 下書きPRとして作成するかどうか

        Returns:
            PullRequest: 作成されたプルリクエストオブジェクト

        Raises:
            GithubException: プルリクエストの作成に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch,
                draft=draft,
            )
            return pr
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"プルリクエストの作成に失敗しました: {error_message}"
            )

    def list_issues(
        self, repo_full_name: str, state: str = "open", labels: list[str] | None = None
    ) -> list[Issue]:
        """リポジトリのイシュー一覧を取得.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            state: 取得するイシューの状態 ("open", "closed", "all")
            labels: フィルタリングするラベルのリスト

        Returns:
            List[Issue]: イシューのリスト

        Raises:
            GithubException: イシュー一覧の取得に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            issues = list(repo.get_issues(state=state, labels=labels))
            return issues
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"イシューの一覧取得に失敗しました: {error_message}"
            )

    def create_issue(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> Issue:
        """リポジトリに新しいイシューを作成します。

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            title: イシューのタイトル
            body: イシューの説明文
            labels: 付けるラベルのリスト
            assignees: アサインするユーザー名のリスト

        Returns:
            Issue: 作成されたイシューオブジェクト

        Raises:
            GithubException: イシューの作成に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            issue = repo.create_issue(
                title=title, body=body, labels=labels, assignees=assignees
            )
            return issue
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"イシューの作成に失敗しました: {error_message}"
            )

    def get_repo_contents(
        self,
        repo_full_name: str,
        path: str = "",
        ref: str | None = None,
    ) -> list[ContentFile | list]:
        """リポジトリ内の指定パスのコンテンツを取得.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            path: 取得するコンテンツのパス（空文字列ならルートディレクトリ）
            ref: 取得するブランチまたはコミットのリファレンス

        Returns:
            List[Union[ContentFile, List]]: ファイルまたはディレクトリのリスト

        Raises:
            GithubException: コンテンツの取得に失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            contents = repo.get_contents(path, ref=ref)

            if not isinstance(contents, list):
                # 単一ファイルの場合はリストに変換
                contents = [contents]

            return contents
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"パス '{path}' のコンテンツ取得に失敗しました: {error_message}",
            )

    @staticmethod
    def create_pr_link(repository: str, pr_number: str) -> str:
        """GitHubのPRへのリンクを生成します.

        Args:
            repository: リポジトリ名 (例: "Finatext/ai-contest-hanare-banare")
            pr_number: PR番号

        Returns:
            str: PRへのリンクURL
        """
        return f"https://github.com/{repository}/pull/{pr_number}"

    def get_pr_info(self, repository: str, pr_number: str) -> dict[str, Any]:
        """PRの詳細情報を取得します。

        Args:
            repository: リポジトリ名 (例: "Finatext/ai-contest-hanare-banare")
            pr_number: PR番号

        Returns:
            Dict[str, Any]: PR情報を含む辞書
                - title: PRのタイトル
                - body: PRの本文
                - author: PR作成者のユーザー名
                - created_at: PR作成日時
                - updated_at: PR最終更新日時
                - merged: マージ済みかどうか
                - mergeable: マージ可能かどうか
                - url: PRのURL

        Raises:
            GithubException: PRが見つからないか、アクセスできない場合
        """
        try:
            repo = self.get_repository(repository)
            pr = repo.get_pull(int(pr_number))

            return {
                "title": pr.title,
                "body": pr.body,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "url": pr.html_url,
            }
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"PR '{pr_number}' の情報取得に失敗しました: {error_message}"
            )

    def commit_untracked_files(
        self,
        repo_full_name: str,
        branch: str,
        file_paths: list[str],
        commit_message: str = "generated by branch-agent",
        working_branch: str = "main",
    ) -> dict[str, Any]:
        """未コミットのファイルをコミットしてプッシュする.

        Args:
            repo_full_name: 'ユーザー名/リポジトリ名' 形式のリポジトリ名
            branch: コミット先のブランチ名
            file_paths: コミットするファイルパスのリスト
            commit_message: コミットメッセージ
            working_branch: 作業ブランチ名
        Returns:
            Dict[str, Any]: コミット結果の情報を含む辞書
                - commit: コミット情報
                - files: 処理されたファイルのリスト

        Raises:
            GithubException: コミットに失敗した場合
        """
        try:
            repo = self.get_repository(repo_full_name)
            print(f"repo: {repo}")

            # 作業ブランチが存在するか確認
            try:
                repo.get_git_ref(f"heads/{working_branch}")
            except GithubException as e:
                if e.status == 404:
                    raise GithubException(
                        e.status, f"ブランチ '{working_branch}' が存在しません"
                    )

            # GitHubのCreateCommitメソッドで必要な情報を構築
            git_ref = repo.get_git_ref(f"heads/{working_branch}")
            base_commit = repo.get_git_commit(git_ref.object.sha)
            base_tree = base_commit.tree
            element_list = []

            # カレントディレクトリを取得 (これをリポジトリルートとみなす)
            repo_root = os.getcwd()
            logger.info(f"リポジトリルート: {repo_root}")
            processed_file_paths = []

            # 各ファイルをコミットに追加
            for file_path in file_paths:
                logger.info(f"処理中のファイルパス: {file_path}")

                # ファイルの存在確認
                if not os.path.exists(file_path):
                    logger.warning(f"警告: ファイルが存在しません: {file_path}")
                    continue

                # 絶対パスをリポジトリルートからの相対パスに変換
                if os.path.isabs(file_path):
                    try:
                        repo_relative_path = os.path.relpath(file_path, repo_root)
                        logger.info(f"リポジトリ相対パス: {repo_relative_path}")
                    except ValueError:
                        logger.warning(
                            f"警告: ファイルパスをリポジトリ相対パスに変換できません: {file_path}"
                        )
                        continue
                else:
                    repo_relative_path = file_path

                with open(file_path, "rb") as f:
                    content = f.read()

                # GitHubにBlobを作成
                blob = repo.create_git_blob(
                    base64.b64encode(content).decode("utf-8"), "base64"
                )

                # ツリー要素を作成
                element = InputGitTreeElement(
                    path=repo_relative_path,  # リポジトリ内の相対パスを使用
                    mode="100644",  # 通常ファイルのモード
                    type="blob",
                    sha=blob.sha,
                )
                element_list.append(element)
                processed_file_paths.append(repo_relative_path)

            if not element_list:
                raise ValueError("コミットするファイルがありません")

            # 新しいツリーを作成
            new_tree = repo.create_git_tree(element_list, base_tree)

            # 現在のコミットを取得
            parent = repo.get_git_ref(f"heads/{branch}").object.sha
            parent_commit = repo.get_git_commit(parent)

            # 新しいコミットを作成
            new_commit = repo.create_git_commit(
                commit_message, new_tree, [parent_commit]
            )

            # ブランチの参照を更新
            repo.get_git_ref(f"heads/{branch}").edit(new_commit.sha)

            result = {
                "commit": {
                    "sha": new_commit.sha,
                    "message": commit_message,
                },
                "files": processed_file_paths,
            }

            return result
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status, f"未コミットファイルのコミットに失敗しました: {error_message}"
            )
        except Exception as e:
            raise Exception(
                f"未コミットファイルのコミット中にエラーが発生しました: {str(e)}"
            )
