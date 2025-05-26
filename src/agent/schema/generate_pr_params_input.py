from pydantic import Field

from src.application.schema.base import BaseInput


class GeneratePRParamsInput(BaseInput):
    """Input data for generating pull request parameters"""

    instruction: str = Field(..., description="Instructions to the programmer")
    programmer_output: str = Field(..., description="Output from the programmer")
    diff: str = Field(default="", description="Code diff (optional)")
