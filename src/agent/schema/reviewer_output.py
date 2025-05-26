from typing import List

from pydantic import Field

from src.application.schema.base import BaseOutput


class ReviewerOutput(BaseOutput):
    """
    Output data after code review
    """

    summary: str = Field(..., description="Review summary comment")
    suggestions: List[str] = Field(
        default_factory=list,
        description="List of discovered issues and improvement suggestions",
    )
    lgtm: bool = Field(..., description="True if no issues (Looks Good To Me)")
