from pydantic import Field

from src.application.schema.base import BaseOutput


# Output schema definition
class ProgrammerOutput(BaseOutput):
    """Output schema for programmer agent"""

    result: str = Field(description="Response result from agent")
