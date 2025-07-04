from pydantic import Field

from src.application.schema.base import BaseInput


class GeneratePullRequestParamsInput(BaseInput):
    """Input for generating pull request parameters"""

    title: str = Field(..., description="PR title")
    description: str = Field(..., description="PR description")
    branch_name: str = Field(..., description="Branch name to create PR")
