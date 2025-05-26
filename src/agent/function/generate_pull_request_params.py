from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.generate_pull_request_params_input import (
    GeneratePullRequestParamsInput,
)
from src.application.function.base import BaseFunction


class GeneratePullRequestParamsFunction(BaseFunction):
    """Function to generate pull request parameters"""

    def __init__(self):
        self.title: str = ""
        self.description: str = ""
        self.branch_name: str = ""

    def execute(self, title: str, description: str, branch_name: str) -> Dict[str, str]:
        self.title = title
        self.description = description
        self.branch_name = branch_name

        return {"result": "success"}

    @classmethod
    def to_tool(cls: Type["GeneratePullRequestParamsFunction"]) -> StructuredTool:
        instance = cls()

        def wrapper(**kwargs):
            return instance.execute(**kwargs)

        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Generates title, description, and branch name for Pull Request.",
            func=wrapper,
            args_schema=GeneratePullRequestParamsInput,
        )
