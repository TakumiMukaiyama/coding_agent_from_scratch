from pydantic import Field

from src.application.schema.base import BaseInput


class ExecRspecTestInput(BaseInput):
    """Input for executing RSpec tests"""

    file_or_dir_path: str = Field(
        ..., description="Path to the file or directory to execute RSpec"
    )
