import glob
from typing import Dict, List, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.get_files_list_input import GetFilesListInput
from src.application.function.base import BaseFunction


class GetFilesListFunction(BaseFunction):
    @staticmethod
    def execute() -> Dict[str, List[str]]:
        files_list = glob.glob("**/*.md", recursive=True) + glob.glob("**/*.tf", recursive=True)
        return {"files_list": files_list}

    @classmethod
    def to_tool(cls: Type["GetFilesListFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="プロジェクト配下の.mdファイルおよび.tfファイル一覧を取得します。",
            func=cls.execute,
            args_schema=GetFilesListInput,
        )
