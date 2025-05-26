import os
from typing import Dict, Type

from langchain_core.tools import StructuredTool

from src.application.function.base import BaseFunction
from src.agent.schema.make_new_file_input import MakeNewFileInput


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
            description="新しいファイルを作成し、指定された内容で書き込みます。",
            func=cls.execute,
            args_schema=MakeNewFileInput,
        )
