import os
from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.make_new_file_input import MakeNewFileInput
from src.application.function.base import BaseFunction


class MakeNewFileFunction(BaseFunction):
    """Function to create a new file"""

    @staticmethod
    def execute(filepath: str, file_contents: str) -> Dict[str, str]:
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(file_contents)

        return {"result": "success"}

    @classmethod
    def to_tool(cls: Type["MakeNewFileFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Creates a new file and writes the specified content to it.",
            func=cls.execute,
            args_schema=MakeNewFileInput,
        )
