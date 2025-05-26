import os
from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.read_file_input import ReadFileInput
from src.application.function.base import BaseFunction


class ReadFileFunction(BaseFunction):
    """Function to read a file"""
    @staticmethod
    def execute(filepath: str) -> Dict[str, str]:
        """Read the contents of a file"""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                contents = f.read()
            return {
                "filepath": filepath,
                "file_contents": contents,
            }
        else:
            return {
                "filepath": filepath,
                "error": "File not found.",
            }

    @classmethod
    def to_tool(cls: Type["ReadFileFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Reads the specified file and returns its contents.",
            func=cls.execute,
            args_schema=ReadFileInput,
        )
