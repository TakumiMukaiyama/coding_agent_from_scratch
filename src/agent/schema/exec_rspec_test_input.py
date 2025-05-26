from pydantic import Field
from src.application.schema.base import BaseInput


class ExecRspecTestInput(BaseInput):
    file_or_dir_path: str = Field(..., description="RSpecを実行するファイルまたはディレクトリのパス")
