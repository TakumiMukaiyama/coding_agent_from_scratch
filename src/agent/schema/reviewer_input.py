from typing import Optional

from pydantic import Field

from src.application.schema.base import BaseInput


class ReviewerInput(BaseInput):
    """
    Input data for code review
    """

    diff: str = Field(..., description="Code diff to be reviewed (Unified Diff format)")
    programmer_comment: Optional[str] = Field(
        None, description="Supplementary explanation from programmer (optional)"
    )
