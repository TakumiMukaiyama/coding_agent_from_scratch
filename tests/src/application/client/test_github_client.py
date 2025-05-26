import unittest
from unittest.mock import MagicMock, patch, Mock
import base64
import json
from github import GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
from github.Branch import Branch
from github.PullRequest import PullRequest
from github.Issue import Issue

from src.application.client.github_client import GitHubClient


class TestGitHubClient(unittest.TestCase):
    """GitHubClientクラスのテスト"""

    def setUp(self):
        """各テスト実行前の準備"""
        self.access_token = "dummy_token"
        self.client = GitHubClient(self.access_token)
        self.repo_full_name = "user/repo"

    @patch("src.application.client.github_client.Github")
    def test_init(self, mock_github):
        """初期化のテスト"""
        client = GitHubClient(self.access_token)
        mock_github.assert_called_once_with(self.access_token)

    @patch.object(GitHubClient, "get_repository")
    def test_get_repository(self, mock_get_repository):
        """リポジトリ取得のテスト"""
        # 正常系
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        repo = self.client.get_repository(self.repo_full_name)

        self.assertEqual(repo, mock_repo)
        mock_get_repository.assert_called_once_with(self.repo_full_name)

    @patch.object(GitHubClient, "get_repository")
    def test_get_repository_error(self, mock_get_repository):
        """リポジトリ取得エラーのテスト"""
        # エラー系
        error = GithubException(404, {"message": "Repository not found"})
        mock_get_repository.side_effect = error

        with self.assertRaises(GithubException) as context:
            self.client.get_repository(self.repo_full_name)

        self.assertEqual(context.exception.status, 404)
        self.assertIn(
            f"リポジトリ '{self.repo_full_name}' の取得に失敗",
            str(context.exception.data),
        )

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_content(self, mock_get_repository):
        """ファイル内容取得のテスト"""
        file_path = "path/to/file.txt"
        file_content = "file content"
        encoded_content = base64.b64encode(file_content.encode()).decode()

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # ファイルコンテンツのモック
        mock_content = MagicMock(spec=ContentFile)
        mock_content.content = encoded_content
        mock_repo.get_contents.return_value = mock_content

        content = self.client.get_file_content(self.repo_full_name, file_path)

        self.assertEqual(content, file_content)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(file_path, ref=None)

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_content_directory_error(self, mock_get_repository):
        """ディレクトリを指定した場合のエラーテスト"""
        file_path = "path/to/directory"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # ディレクトリの場合はリストが返される
        mock_repo.get_contents.return_value = [
            MagicMock(spec=ContentFile),
            MagicMock(spec=ContentFile),
        ]

        with self.assertRaises(ValueError) as context:
            self.client.get_file_content(self.repo_full_name, file_path)

        self.assertIn("はディレクトリです", str(context.exception))

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_content_error(self, mock_get_repository):
        """ファイル内容取得エラーのテスト"""
        file_path = "path/to/file.txt"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # エラーを発生させる
        error = GithubException(404, {"message": "File not found"})
        mock_repo.get_contents.side_effect = error

        with self.assertRaises(GithubException) as context:
            self.client.get_file_content(self.repo_full_name, file_path)

        self.assertEqual(context.exception.status, 404)
        self.assertIn(
            f"ファイル '{file_path}' の取得に失敗", str(context.exception.data)
        )

    @patch.object(GitHubClient, "get_repository")
    def test_create_file(self, mock_get_repository):
        """ファイル作成のテスト"""
        file_path = "path/to/file.txt"
        content = "new file content"
        commit_message = "test commit"
        branch = "test-branch"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # create_fileの戻り値
        expected_result = {
            "commit": {"sha": "commit_sha"},
            "content": {"sha": "content_sha"},
        }
        mock_repo.create_file.return_value = expected_result

        result = self.client.create_file(
            self.repo_full_name, file_path, content, commit_message, branch
        )

        self.assertEqual(result, expected_result)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.create_file.assert_called_once_with(
            path=file_path,
            message=commit_message,
            content=content.encode("utf-8"),
            branch=branch,
        )

    @patch.object(GitHubClient, "get_repository")
    def test_update_file(self, mock_get_repository):
        """ファイル更新のテスト"""
        file_path = "path/to/file.txt"
        content = "updated file content"
        commit_message = "update commit"
        sha = "file_sha"
        branch = "test-branch"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # update_fileの戻り値
        expected_result = {
            "commit": {"sha": "commit_sha"},
            "content": {"sha": "content_sha"},
        }
        mock_repo.update_file.return_value = expected_result

        result = self.client.update_file(
            self.repo_full_name, file_path, content, commit_message, sha, branch
        )

        self.assertEqual(result, expected_result)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.update_file.assert_called_once_with(
            path=file_path,
            message=commit_message,
            content=content.encode("utf-8"),
            sha=sha,
            branch=branch,
        )

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_sha(self, mock_get_repository):
        """ファイルSHA取得のテスト"""
        file_path = "path/to/file.txt"
        expected_sha = "file_sha_123"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # ファイルコンテンツのモック
        mock_content = MagicMock(spec=ContentFile)
        mock_content.sha = expected_sha
        mock_repo.get_contents.return_value = mock_content

        sha = self.client.get_file_sha(self.repo_full_name, file_path)

        self.assertEqual(sha, expected_sha)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(file_path, ref=None)

    @patch.object(GitHubClient, "get_repository")
    def test_create_branch(self, mock_get_repository):
        """ブランチ作成のテスト"""
        new_branch_name = "new-branch"
        base_branch = "main"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # 基になるブランチリファレンスのモック
        mock_ref = MagicMock()
        mock_ref.object.sha = "base_commit_sha"
        mock_repo.get_git_ref.return_value = mock_ref

        # 新しいブランチのモック
        mock_branch = MagicMock(spec=Branch)
        mock_repo.get_branch.return_value = mock_branch

        branch = self.client.create_branch(
            self.repo_full_name, new_branch_name, base_branch
        )

        self.assertEqual(branch, mock_branch)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_git_ref.assert_called_once_with(f"heads/{base_branch}")
        mock_repo.create_git_ref.assert_called_once_with(
            ref=f"refs/heads/{new_branch_name}", sha="base_commit_sha"
        )
        mock_repo.get_branch.assert_called_once_with(new_branch_name)

    @patch.object(GitHubClient, "get_repository")
    def test_create_branch_default_base(self, mock_get_repository):
        """デフォルトブランチを基にしたブランチ作成のテスト"""
        new_branch_name = "new-branch"
        default_branch = "main"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_repo.default_branch = default_branch
        mock_get_repository.return_value = mock_repo

        # 基になるブランチリファレンスのモック
        mock_ref = MagicMock()
        mock_ref.object.sha = "base_commit_sha"
        mock_repo.get_git_ref.return_value = mock_ref

        # 新しいブランチのモック
        mock_branch = MagicMock(spec=Branch)
        mock_repo.get_branch.return_value = mock_branch

        branch = self.client.create_branch(self.repo_full_name, new_branch_name)

        self.assertEqual(branch, mock_branch)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_git_ref.assert_called_once_with(f"heads/{default_branch}")

    @patch.object(GitHubClient, "get_repository")
    def test_list_branches(self, mock_get_repository):
        """ブランチ一覧取得のテスト"""
        branch_names = ["main", "develop", "feature/test"]

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # ブランチのモック
        mock_branches = []
        for name in branch_names:
            mock_branch = MagicMock(spec=Branch)
            mock_branch.name = name
            mock_branches.append(mock_branch)

        mock_repo.get_branches.return_value = mock_branches

        branches = self.client.list_branches(self.repo_full_name)

        self.assertEqual(branches, branch_names)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_branches.assert_called_once()

    @patch.object(GitHubClient, "get_repository")
    def test_create_pull_request(self, mock_get_repository):
        """プルリクエスト作成のテスト"""
        title = "Test PR"
        body = "This is a test PR"
        head_branch = "feature/test"
        base_branch = "main"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # プルリクエストのモック
        mock_pr = MagicMock(spec=PullRequest)
        mock_repo.create_pull.return_value = mock_pr

        pr = self.client.create_pull_request(
            self.repo_full_name, title, body, head_branch, base_branch
        )

        self.assertEqual(pr, mock_pr)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.create_pull.assert_called_once_with(
            title=title, body=body, head=head_branch, base=base_branch, draft=False
        )

    @patch.object(GitHubClient, "get_repository")
    def test_list_issues(self, mock_get_repository):
        """イシュー一覧取得のテスト"""
        state = "open"
        labels = ["bug", "feature"]

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # イシューのモック
        mock_issue1 = MagicMock(spec=Issue)
        mock_issue2 = MagicMock(spec=Issue)
        mock_issues = [mock_issue1, mock_issue2]
        mock_repo.get_issues.return_value = mock_issues

        issues = self.client.list_issues(self.repo_full_name, state, labels)

        self.assertEqual(issues, mock_issues)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_issues.assert_called_once_with(state=state, labels=labels)

    @patch.object(GitHubClient, "get_repository")
    def test_create_issue(self, mock_get_repository):
        """イシュー作成のテスト"""
        title = "Test Issue"
        body = "This is a test issue"
        labels = ["bug"]
        assignees = ["user1"]

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # イシューのモック
        mock_issue = MagicMock(spec=Issue)
        mock_repo.create_issue.return_value = mock_issue

        issue = self.client.create_issue(
            self.repo_full_name, title, body, labels, assignees
        )

        self.assertEqual(issue, mock_issue)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.create_issue.assert_called_once_with(
            title=title, body=body, labels=labels, assignees=assignees
        )

    @patch.object(GitHubClient, "get_repository")
    def test_get_repo_contents(self, mock_get_repository):
        """リポジトリコンテンツ取得のテスト"""
        path = "path/to/dir"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # コンテンツのモック
        mock_content1 = MagicMock(spec=ContentFile)
        mock_content2 = MagicMock(spec=ContentFile)
        mock_contents = [mock_content1, mock_content2]
        mock_repo.get_contents.return_value = mock_contents

        contents = self.client.get_repo_contents(self.repo_full_name, path)

        self.assertEqual(contents, mock_contents)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(path, ref=None)

    @patch.object(GitHubClient, "get_repository")
    def test_get_repo_contents_single_file(self, mock_get_repository):
        """単一ファイルのリポジトリコンテンツ取得のテスト"""
        path = "path/to/file.txt"

        # リポジトリのモック
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # 単一ファイルのコンテンツのモック
        mock_content = MagicMock(spec=ContentFile)
        mock_repo.get_contents.return_value = mock_content

        contents = self.client.get_repo_contents(self.repo_full_name, path)

        self.assertEqual(contents, [mock_content])  # リストに変換されていることを確認
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(path, ref=None)


if __name__ == "__main__":
    unittest.main()
