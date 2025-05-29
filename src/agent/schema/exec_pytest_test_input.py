from pydantic import Field

from src.application.schema.base import BaseInput


class ExecPytestTestInput(BaseInput):
    """Input for executing pytest tests"""

    file_or_dir_path: str = Field(..., description="Path to the file or directory to execute pytest")
