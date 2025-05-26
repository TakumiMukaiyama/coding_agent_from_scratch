from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.over_write_input import OverwriteFileInput
from src.application.function.base import BaseFunction


class OverwriteFileFunction(BaseFunction):
    """Function to overwrite a file"""
    @staticmethod
    def execute(filepath: str, new_text: str) -> Dict[str, str]:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_text)

        return {"result": "success"}

    @classmethod
    def to_tool(cls: Type["OverwriteFileFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Overwrites the specified file with new content.",
            func=cls.execute,
            args_schema=OverwriteFileInput,
        )
