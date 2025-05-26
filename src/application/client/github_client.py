"""Client class for interacting with GitHub repositories.
Communicates with GitHub API using PyGithub library.
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

from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """Client class for interacting with GitHub API.

    Provides common GitHub operations including authentication, repository operations,
    file operations, branch operations, and creation of PRs and issues.
    """

    def __init__(self, access_token: str | None = None):
        """Initialize GitHub API client.

        Args:
            access_token: GitHub personal access token (optional).
                          If not specified, it will be retrieved from the GITHUB_TOKEN environment variable.
        """
        if access_token is None:
            access_token = os.environ.get("GITHUB_TOKEN")
            if not access_token:
                print(
                    "Environment variable GITHUB_TOKEN is not set. GitHub operations cannot be performed."
                )
                sys.exit(1)

        self.github = Github(access_token)

    def get_repository(self, repo_full_name: str) -> Repository:
        """Get repository by specified name.

        Args:
            repo_full_name: Repository name in 'username/repository' format
        Returns:
            Repository: Retrieved repository object
        Raises:
            GithubException: When repository is not found or access is denied
        """
        try:
            return self.github.get_repo(repo_full_name)
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"Failed to retrieve repository '{repo_full_name}': {error_message}",
            )

    def get_file_content(
        self, repo_full_name: str, file_path: str, ref: str | None = None
    ) -> str:
        """Get the content of the specified file in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            file_path: Path of file to get
            ref: Reference of branch or commit to get (default: repository's default branch)
        Returns:
            str: File content
        Raises:
            GithubException: When file is not found or access is denied
        """
        try:
            repo = self.get_repository(repo_full_name)
            content_file = repo.get_contents(file_path, ref=ref)

            if isinstance(content_file, list):
                raise ValueError(
                    f"'{file_path}' is a directory. Please specify a file path."
                )

            # Decode file content
            content = base64.b64decode(content_file.content).decode("utf-8")
            return content
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"Failed to get file '{file_path}': {error_message}",
            )

    def create_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Create a new file in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            file_path: Path of file to create
            content: File content
            commit_message: Commit message
            branch: Branch name to create file (default: repository's default branch)

        Returns:
            Dict: Dictionary containing creation result information

        Raises:
            GithubException: When file creation fails
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
                f"Failed to create file '{file_path}': {error_message}",
            )

    def update_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        branch: str,
        commit_message: str = "agent-update",
    ) -> dict[str, Any]:
        """Update existing file in repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            file_path: Path of file to update
            content: New file content
            commit_message: Commit message
            branch: Branch name to update file (default: repository's default branch)

        Returns:
            Dict: Dictionary containing update result information

        Raises:
            GithubException: When file update fails
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
                f"Failed to update file '{file_path}': {error_message}",
            )

    def get_file_sha(
        self, repo_full_name: str, file_path: str, ref: str | None = None
    ) -> str:
        """Get the SHA value of the specified file.

        Required for file updates.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            file_path: Path of file to get
            ref: Reference of branch or commit to get (default: repository's default branch)

        Returns:
            str: SHA value of the file

        Raises:
            GithubException: When file is not found or access is denied
        """
        try:
            repo = self.get_repository(repo_full_name)
            content_file = repo.get_contents(file_path, ref=ref)

            if isinstance(content_file, list):
                raise ValueError(
                    f"'{file_path}' is a directory. Please specify a file path."
                )

            return content_file.sha
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"Failed to get SHA of file '{file_path}': {error_message}",
            )

    def create_branch(
        self, repo_full_name: str, new_branch_name: str, base_branch: str | None = None
    ) -> Branch:
        """Create a new branch based on an existing branch.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            new_branch_name: Name of new branch to create
            base_branch: Name of branch to base on (default: repository's default branch)

        Returns:
            Branch: Created branch object

        Raises:
            GithubException: When branch creation fails
        """
        try:
            repo = self.get_repository(repo_full_name)

            # If base branch is not specified, use the default branch
            if base_branch is None:
                base_branch = repo.default_branch

            # Get the reference of the base branch
            base_branch_ref = repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_branch_ref.object.sha

            # Create a new branch
            repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_sha)

            # Return the created branch
            return repo.get_branch(new_branch_name)
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"Failed to create branch '{new_branch_name}': {error_message}",
            )

    def list_branches(self, repo_full_name: str) -> list[str]:
        """Get the list of branches in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format

        Returns:
            List[str]: List of branch names

        Raises:
            GithubException: When branch list retrieval fails
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
                e.status, f"Failed to get branch list: {error_message}"
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
        """Create a pull request in the repository.

        Args:
            title: Title of PR
            body: Description of PR
            head_branch: Branch containing changes
            base_branch: Branch to merge into
            draft: Whether to create as a draft PR

        Returns:
            PullRequest: Created pull request object

        Raises:
            GithubException: When pull request creation fails
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
                e.status, f"Failed to create pull request: {error_message}"
            )

    def list_issues(
        self, repo_full_name: str, state: str = "open", labels: list[str] | None = None
    ) -> list[Issue]:
        """Get the list of issues in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            state: State of issue to get ("open", "closed", "all")
            labels: List of labels to filter

        Returns:
            List[Issue]: List of issues

        Raises:
            GithubException: When issue list retrieval fails
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
                e.status, f"Failed to get issue list: {error_message}"
            )

    def create_issue(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> Issue:
        """Create a new issue in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            title: Title of issue
            body: Description of issue
            labels: List of labels to add
            assignees: List of users to assign

        Returns:
            Issue: Created issue object

        Raises:
            GithubException: When issue creation fails
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
            raise GithubException(e.status, f"Failed to create issue: {error_message}")

    def get_repo_contents(
        self,
        repo_full_name: str,
        path: str = "",
        ref: str | None = None,
    ) -> list[ContentFile | list]:
        """Get the contents of the specified path in the repository.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            path: Path of content to get (empty string for root directory)
            ref: Reference of branch or commit to get

        Returns:
            List[Union[ContentFile, List]]: List of files or directories

        Raises:
            GithubException: When content retrieval fails
        """
        try:
            repo = self.get_repository(repo_full_name)
            contents = repo.get_contents(path, ref=ref)

            if not isinstance(contents, list):
                # If it is a single file, convert it to a list
                contents = [contents]

            return contents
        except GithubException as e:
            error_message = (
                e.data.get("message", "") if isinstance(e.data, dict) else str(e.data)
            )
            raise GithubException(
                e.status,
                f"Failed to get contents of path '{path}': {error_message}",
            )

    @staticmethod
    def create_pr_link(repository: str, pr_number: str) -> str:
        """Generate a link to a PR on GitHub.

        Args:
            repository: Repository name in 'username/repository' format
            pr_number: PR number

        Returns:
            str: Link to PR
        """
        return f"https://github.com/{repository}/pull/{pr_number}"

    def get_pr_info(self, repository: str, pr_number: str) -> dict[str, Any]:
        """Get the detailed information of a PR.

        Args:
            repository: Repository name in 'username/repository' format
            pr_number: PR number

        Returns:
            Dict[str, Any]: Dictionary containing PR information
                - title: PR title
                - body: PR body
                - author: PR author's username
                - created_at: PR creation time
                - updated_at: PR last updated time
                - merged: Whether it is merged
                - mergeable: Whether it is mergeable
                - url: PR URL

        Raises:
            GithubException: When PR is not found or access is denied
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
                e.status,
                f"Failed to get information of PR '{pr_number}': {error_message}",
            )

    def commit_untracked_files(
        self,
        repo_full_name: str,
        branch: str,
        file_paths: list[str],
        commit_message: str = "generated by branch-agent",
        working_branch: str = "main",
    ) -> dict[str, Any]:
        """Commit and push untracked files.

        Args:
            repo_full_name: Repository name in 'username/repository' format
            branch: Name of branch to commit to
            file_paths: List of file paths to commit
            commit_message: Commit message
            working_branch: Name of working branch
        Returns:
            Dict[str, Any]: Dictionary containing commit result information
                - commit: Commit information
                - files: List of processed files

        Raises:
            GithubException: When commit fails
        """
        try:
            repo = self.get_repository(repo_full_name)
            print(f"repo: {repo}")

            # Check if the working branch exists
            try:
                repo.get_git_ref(f"heads/{working_branch}")
            except GithubException as e:
                if e.status == 404:
                    raise GithubException(
                        e.status, f"Branch '{working_branch}' does not exist"
                    )

            # Build necessary information for GitHub's CreateCommit method
            git_ref = repo.get_git_ref(f"heads/{working_branch}")
            base_commit = repo.get_git_commit(git_ref.object.sha)
            base_tree = base_commit.tree
            element_list = []

            # Get the current directory (this is considered the repository root)
            repo_root = os.getcwd()
            logger.info(f"Repository root: {repo_root}")
            processed_file_paths = []

            # Add each file to the commit
            for file_path in file_paths:
                logger.info(f"Processing file path: {file_path}")

                # Check if the file exists
                if not os.path.exists(file_path):
                    logger.warning(f"Warning: File does not exist: {file_path}")
                    continue

                # Convert absolute path to relative path from repository root
                if os.path.isabs(file_path):
                    try:
                        repo_relative_path = os.path.relpath(file_path, repo_root)
                        logger.info(f"Repository relative path: {repo_relative_path}")
                    except ValueError:
                        logger.warning(
                            f"Warning: Failed to convert file path to repository relative path: {file_path}"
                        )
                        continue
                else:
                    repo_relative_path = file_path

                with open(file_path, "rb") as f:
                    content = f.read()

                # Create a blob in GitHub
                blob = repo.create_git_blob(
                    base64.b64encode(content).decode("utf-8"), "base64"
                )

                # Create a tree element
                element = InputGitTreeElement(
                    path=repo_relative_path,  # Use relative path in repository
                    mode="100644",  # Mode for normal file
                    type="blob",
                    sha=blob.sha,
                )
                element_list.append(element)
                processed_file_paths.append(repo_relative_path)

            if not element_list:
                raise ValueError("No files to commit")

            # Create a new tree
            new_tree = repo.create_git_tree(element_list, base_tree)

            # Get the current commit
            parent = repo.get_git_ref(f"heads/{branch}").object.sha
            parent_commit = repo.get_git_commit(parent)

            # Create a new commit
            new_commit = repo.create_git_commit(
                commit_message, new_tree, [parent_commit]
            )

            # Update the branch reference
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
                e.status, f"Failed to commit untracked files: {error_message}"
            )
        except Exception as e:
            raise Exception(
                f"Error occurred while committing untracked files: {str(e)}"
            )
