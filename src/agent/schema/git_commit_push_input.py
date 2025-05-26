from pydantic import Field

from src.application.schema.base import BaseInput


class GitCommitPushInput(BaseInput):
    """Input data for Git commit & push"""

    path_to_add: str = Field(
        default=".", description="Path to add (default is all changes)"
    )
    commit_message: str = Field(
        default="", description="Commit message (auto-generated if empty)"
    )
    remote_name: str = Field(default="origin", description="Remote name")
    branch_name: str = Field(
        default="", description="Branch name to push to (current branch if empty)"
    )
    force_push: bool = Field(default=False, description="Whether to force push")
