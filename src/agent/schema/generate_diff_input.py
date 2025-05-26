from src.application.schema.base import BaseInput
from pydantic import Field


class GenerateDiffInput(BaseInput):
    """Input for generating diff"""

    base_branch: str = Field(
        default="main", description="Name of the base branch (default is main)"
    )
    target_branch: str | None = Field(
        default=None,
        description="Name of the target branch (default is current branch)",
    )
    file_path: str | None = Field(
        default=None, description="Specific file path (if not specified, all files)"
    )
