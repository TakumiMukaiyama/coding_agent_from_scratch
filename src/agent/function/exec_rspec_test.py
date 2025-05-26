import subprocess
from typing import Dict, Type
from langchain_core.tools import StructuredTool

from src.application.function.base import BaseFunction
from src.agent.schema.exec_rspec_test_input import ExecRspecTestInput


class ExecRspecTestFunction(BaseFunction):
    """Function to execute RSpec tests"""

    @staticmethod
    def execute(file_or_dir_path: str) -> Dict[str, str]:
        script = f"bundle exec rspec '{file_or_dir_path}'"
        try:
            result = subprocess.run(
                script, shell=True, capture_output=True, text=True, check=True
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_status": str(result.returncode),
            }
        except subprocess.CalledProcessError as e:
            return {
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
                "exit_status": str(e.returncode),
            }

    @classmethod
    def to_tool(cls: Type["ExecRspecTestFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Execute RSpec tests on the specified file or directory.",
            func=cls.execute,
            args_schema=ExecRspecTestInput,
        )
