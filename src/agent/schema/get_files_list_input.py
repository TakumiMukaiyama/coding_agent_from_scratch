from typing import List, Optional

from pydantic import Field

from src.application.schema.base import BaseInput


class GetFilesListInput(BaseInput):
    """Input for getting file list"""

    file_extensions: Optional[List[str]] = Field(
        default=None,
        description="List of file extensions to retrieve (e.g. ['py', 'js', 'ts']). If not specified, get common code files",
    )

    include_patterns: Optional[List[str]] = Field(
        default=None,
        description="List of file patterns to include (e.g. ['**/*.py', 'src/**/*.js'])",
    )

    exclude_patterns: Optional[List[str]] = Field(
        default=None,
        description="List of file patterns to exclude (e.g. ['**/node_modules/**', '**/__pycache__/**'])",
    )

    root_directory: Optional[str] = Field(
        default=".",
        description="Root directory to start search from (default: current directory)",
    )

    max_files: Optional[int] = Field(
        default=1000, description="Maximum number of files to retrieve (default: 1000)"
    )
