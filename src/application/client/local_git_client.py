from git import Repo
from github import GithubException

from src.application.client.github_client import GitHubClient
from src.infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class LocalGitClient:
    """Class for committing, pushing files edited by agent and creating PRs."""

    def __init__(
        self,
        repo_path: str,
        github_token: str,
        repo_full_name: str,
        github_username: str,
    ):
        """Initialize.

        Args:
            repo_path: Path to local repository
            github_token: GitHub access token
            repo_full_name: Repository name in 'username/repository' format
        """
        self.repo_path = repo_path
        self.repo_full_name = repo_full_name
        self.github_token = github_token
        self.github_username = github_username
        self.repo = Repo(repo_path)
        self.github_client = GitHubClient(github_token)

    def commit_changes(self, file_paths: list[str], commit_message: str) -> dict:
        """Commit changes."""
        try:
            self.repo.git.add(file_paths)
            commit = self.repo.index.commit(commit_message)
            logger.info(f"Changes committed: {commit.hexsha}")
            return {
                "commit": {"sha": commit.hexsha, "message": commit_message},
                "files": file_paths,
            }
        except Exception:
            logger.exception()
            raise

    def push_to_remote(self, branch_name: str | None = None) -> bool:
        """Push changes to remote repository (HTTPS authentication using PAT)."""
        try:
            if branch_name is None:
                branch_name = self.repo.active_branch.name

            if "origin" not in [remote.name for remote in self.repo.remotes]:
                raise ValueError("Remote 'origin' is not configured")

            # Replace with URL containing authentication info
            remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.repo_full_name}.git"

            origin = self.repo.remote("origin")
            origin.set_url(remote_url)

            # Execute push
            self.repo.git.push("--set-upstream", "origin", branch_name)
            logger.info(f"Changes pushed to remote: {branch_name}")
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
        """Create a pull request."""
        try:
            if head_branch is None:
                head_branch = self.repo.active_branch.name

            if head_branch == base_branch:
                raise ValueError(f"Base branch '{base_branch}' and head branch '{head_branch}' are the same")

            pr = self.github_client.create_pull_request(
                repo_full_name=self.repo_full_name,
                title=title,
                body=body,
                head_branch=head_branch,
                base_branch=base_branch,
            )

            logger.info(f"PR created: #{pr.number} - {pr.html_url}")
            return {"number": pr.number, "title": pr.title, "url": pr.html_url}

        except GithubException as e:
            error_message = str(e)
            if hasattr(e, "data") and isinstance(e.data, dict):
                msg = e.data.get("message", "")
                errors = e.data.get("errors", [])
                details = ", ".join([err.get("message", str(err)) for err in errors])
                error_message = f"{msg} - {details}" if details else msg

            logger.exception(f"Failed to create PR: {error_message}")
            raise GithubException(e.status, error_message)
        except Exception:
            logger.exception()
            raise
