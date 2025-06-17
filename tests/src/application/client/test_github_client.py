import base64
import unittest
from unittest.mock import MagicMock, patch

from github import GithubException
from github.Branch import Branch
from github.ContentFile import ContentFile
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository

from src.application.client.github_client import GitHubClient


class TestGitHubClient(unittest.TestCase):
    """Test for GitHubClient class"""

    def setUp(self):
        """Setup before tests"""
        self.access_token = "dummy_token"
        self.client = GitHubClient(self.access_token)
        self.repo_full_name = "user/repo"

    @patch("src.application.client.github_client.Github")
    def test_init(self, mock_github):
        """Test for initialization"""
        _ = GitHubClient(self.access_token)
        mock_github.assert_called_once_with(self.access_token)

    @patch.object(GitHubClient, "get_repository")
    def test_get_repository(self, mock_get_repository):
        """Test for get_repository method"""
        # Normal case
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        repo = self.client.get_repository(self.repo_full_name)

        self.assertEqual(repo, mock_repo)
        mock_get_repository.assert_called_once_with(self.repo_full_name)

    @patch.object(GitHubClient, "get_repository")
    def test_get_repository_error(self, mock_get_repository):
        """Test for get_repository method when error occurs"""
        # Error case
        error = GithubException(
            404,
            f"リポジトリ '{self.repo_full_name}' の取得に失敗しました: Repository not found",
        )
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
        """Test for get_file_content method"""
        file_path = "path/to/file.txt"
        file_content = "file content"
        encoded_content = base64.b64encode(file_content.encode()).decode()

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock file content
        mock_content = MagicMock(spec=ContentFile)
        mock_content.content = encoded_content
        mock_repo.get_contents.return_value = mock_content

        content = self.client.get_file_content(self.repo_full_name, file_path)

        self.assertEqual(content, file_content)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(file_path, ref=None)

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_content_directory_error(self, mock_get_repository):
        """Test for get_file_content method when directory is specified"""
        file_path = "path/to/directory"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # If directory is specified, list is returned
        mock_repo.get_contents.return_value = [
            MagicMock(spec=ContentFile),
            MagicMock(spec=ContentFile),
        ]

        with self.assertRaises(ValueError) as context:
            self.client.get_file_content(self.repo_full_name, file_path)

        self.assertIn("はディレクトリです", str(context.exception))

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_content_error(self, mock_get_repository):
        """Test for get_file_content method when error occurs"""
        file_path = "path/to/file.txt"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Raise error
        error = GithubException(404, {"message": "File not found"})
        mock_repo.get_contents.side_effect = error

        with self.assertRaises(GithubException) as context:
            self.client.get_file_content(self.repo_full_name, file_path)

        self.assertEqual(context.exception.status, 404)
        self.assertIn(f"Failed to get file '{file_path}'", str(context.exception.data))

    @patch.object(GitHubClient, "get_repository")
    def test_create_file(self, mock_get_repository):
        """Test for create_file method"""
        file_path = "path/to/file.txt"
        content = "new file content"
        commit_message = "test commit"
        branch = "test-branch"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Return value of create_file
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

    @patch.object(GitHubClient, "get_file_sha")
    @patch.object(GitHubClient, "get_repository")
    def test_update_file(self, mock_get_repository, mock_get_file_sha):
        """Test for update_file method"""
        file_path = "path/to/file.txt"
        content = "updated file content"
        commit_message = "update commit"
        branch = "test-branch"
        sha = "file_sha"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo
        mock_get_file_sha.return_value = sha

        # Return value of update_file
        expected_result = {
            "commit": {"sha": "commit_sha"},
            "content": {"sha": "content_sha"},
        }
        mock_repo.update_file.return_value = expected_result

        result = self.client.update_file(
            self.repo_full_name, file_path, content, branch, commit_message
        )

        self.assertEqual(result, expected_result)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_get_file_sha.assert_called_once_with(
            self.repo_full_name, file_path, branch
        )
        mock_repo.update_file.assert_called_once_with(
            path=file_path,
            message=commit_message,
            content=content.encode("utf-8"),
            sha=sha,
            branch=branch,
        )

    @patch.object(GitHubClient, "get_repository")
    def test_get_file_sha(self, mock_get_repository):
        """Test for get_file_sha method"""
        file_path = "path/to/file.txt"
        expected_sha = "file_sha_123"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock file content
        mock_content = MagicMock(spec=ContentFile)
        mock_content.sha = expected_sha
        mock_repo.get_contents.return_value = mock_content

        sha = self.client.get_file_sha(self.repo_full_name, file_path)

        self.assertEqual(sha, expected_sha)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(file_path, ref=None)

    @patch.object(GitHubClient, "get_repository")
    def test_create_branch(self, mock_get_repository):
        """Test for create_branch method"""
        new_branch_name = "new-branch"
        base_branch = "main"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock base branch reference
        mock_ref = MagicMock()
        mock_ref.object.sha = "base_commit_sha"
        mock_repo.get_git_ref.return_value = mock_ref

        # Mock new branch
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
        """Test for create_branch method when default base branch is specified"""
        new_branch_name = "new-branch"
        default_branch = "main"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_repo.default_branch = default_branch
        mock_get_repository.return_value = mock_repo

        # Mock base branch reference
        mock_ref = MagicMock()
        mock_ref.object.sha = "base_commit_sha"
        mock_repo.get_git_ref.return_value = mock_ref

        # Mock new branch
        mock_branch = MagicMock(spec=Branch)
        mock_repo.get_branch.return_value = mock_branch

        branch = self.client.create_branch(self.repo_full_name, new_branch_name)

        self.assertEqual(branch, mock_branch)
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_git_ref.assert_called_once_with(f"heads/{default_branch}")

    @patch.object(GitHubClient, "get_repository")
    def test_list_branches(self, mock_get_repository):
        """Test for list_branches method"""
        branch_names = ["main", "develop", "feature/test"]

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock branches
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
        """Test for create_pull_request method"""
        title = "Test PR"
        body = "This is a test PR"
        head_branch = "feature/test"
        base_branch = "main"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock pull request
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
        """Test for list_issues method"""
        state = "open"
        labels = ["bug", "feature"]

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock issues
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
        """Test for create_issue method"""
        title = "Test Issue"
        body = "This is a test issue"
        labels = ["bug"]
        assignees = ["user1"]

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock issue
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
        """Test for get_repo_contents method"""
        path = "path/to/dir"

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock contents
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
        """Test for get_repo_contents method when single file is specified"""
        path = "path/to/file.txt"

        mock_repo = MagicMock(spec=Repository)
        mock_get_repository.return_value = mock_repo

        # Mock single file content
        mock_content = MagicMock(spec=ContentFile)
        mock_repo.get_contents.return_value = mock_content

        contents = self.client.get_repo_contents(self.repo_full_name, path)

        self.assertEqual(contents, [mock_content])  # Check that list is returned
        mock_get_repository.assert_called_once_with(self.repo_full_name)
        mock_repo.get_contents.assert_called_once_with(path, ref=None)
    

if __name__ == "__main__":
    unittest.main()
