from typing import Optional

from pydantic import Field

from src.application.schema.base import BaseInput


# 入力スキーマの定義
class ProgrammerInput(BaseInput):
    """プログラマーエージェントへの入力スキーマ"""

    instruction: str = Field(description="ユーザーからの指示")

    language: Optional[str] = Field(
        default="Python",
        description="プログラミング言語（例: Python, JavaScript, TypeScript, Java, Go, Rust, Terraform等）",
    )

    project_type: Optional[str] = Field(
        default="一般的なソフトウェア開発",
        description="プロジェクトタイプ（例: Webアプリケーション, API開発, データ分析, インフラストラクチャ管理等）",
    )

    project_root: Optional[str] = Field(default="src/", description="プロジェクトのルートディレクトリ")

    language_specific_notes: Optional[str] = Field(
        default="", description="言語固有の考慮事項やベストプラクティス（自動生成される場合は空文字列）"
    )
