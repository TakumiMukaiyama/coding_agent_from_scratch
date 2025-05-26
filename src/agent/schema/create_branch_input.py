from src.application.schema.base import BaseInput
from pydantic import Field


class CreateBranchInput(BaseInput):
    """Input for creating a branch"""

    branch_name: str = Field(..., description="Name of the branch to create")
