import os
from typing import Dict, Type
from langchain_core.tools import StructuredTool

from src.application.function.base import BaseFunction
from src.agent.schema.read_file_input import ReadFileInput


class ReadFileFunction(BaseFunction):
    @staticmethod
    def execute(filepath: str) -> Dict[str, str]:
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
            description="指定されたファイルを読み取り、内容を返します。",
            func=cls.execute,
            args_schema=ReadFileInput,
        )
