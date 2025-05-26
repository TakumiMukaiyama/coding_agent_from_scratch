from typing import Optional

from pydantic import Field

from src.application.schema.base import BaseInput


# Input schema definition
class ProgrammerInput(BaseInput):
    """Input schema for programmer agent"""

    instruction: str = Field(description="Instructions from user")

    language: Optional[str] = Field(
        default="Python",
        description="Programming language (e.g., Python, JavaScript, TypeScript, Java, Go, Rust, Terraform, etc.)",
    )

    project_type: Optional[str] = Field(
        default="General software development",
        description="Project type (e.g., Web application, API development, Data analysis, Infrastructure management, etc.)",
    )

    project_root: Optional[str] = Field(default="src/", description="Root directory of the project")

    language_specific_notes: Optional[str] = Field(
        default="",
        description="Language-specific considerations and best practices (empty string if auto-generated)",
    )
