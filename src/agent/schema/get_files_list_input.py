from typing import List, Optional

from pydantic import Field

from src.application.schema.base import BaseInput


class GetFilesListInput(BaseInput):
    """ファイル一覧取得の入力スキーマ"""

    file_extensions: Optional[List[str]] = Field(
        default=None,
        description="取得するファイルの拡張子リスト（例: ['py', 'js', 'ts']）。指定しない場合は一般的なコードファイルを取得",
    )

    include_patterns: Optional[List[str]] = Field(
        default=None, description="含めるファイルパターンのリスト（例: ['**/*.py', 'src/**/*.js']）"
    )

    exclude_patterns: Optional[List[str]] = Field(
        default=None, description="除外するファイルパターンのリスト（例: ['**/node_modules/**', '**/__pycache__/**']）"
    )

    root_directory: Optional[str] = Field(
        default=".", description="検索を開始するルートディレクトリ（デフォルト: 現在のディレクトリ）"
    )

    max_files: Optional[int] = Field(default=1000, description="取得するファイル数の上限（デフォルト: 1000）")
