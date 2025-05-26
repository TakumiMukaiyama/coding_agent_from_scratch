"""
汎用プロンプトテンプレート設定

このモジュールは任意のプログラミング言語とプロジェクトタイプに対応した
プロンプトテンプレートを提供します。

使用例:
    # Python プロジェクトの場合
    from src.agent.schema.programmer_input import ProgrammerInput

    input_data = ProgrammerInput(
        instruction="新しいAPIエンドポイントを作成してください",
        language="Python",
        project_type="Webアプリケーション",
        project_root="src/"
    )

    # TypeScript プロジェクトの場合
    input_data = ProgrammerInput(
        instruction="新しいコンポーネントを作成してください",
        language="TypeScript",
        project_type="React アプリケーション",
        project_root="frontend/"
    )

    # Terraform プロジェクトの場合
    input_data = ProgrammerInput(
        instruction="新しいリソースを定義してください",
        language="Terraform",
        project_type="インフラストラクチャ管理",
        project_root="terraform/"
    )

    # 言語固有の設定を取得
    config = get_language_config("python")
    print(config["test_command"])  # "pytest"
"""

# プロンプトテンプレートの定義
PROGRAMMER_PROMPT_TEMPLATE = """
あなたは '{project_root}' ディレクトリをルートとする{language}プロジェクトのプログラマーエージェントです。
以下のユーザー指示に従ってファイルを編集してください。

## プロジェクト情報
- プログラミング言語: {language}
- プロジェクトタイプ: {project_type}
- ルートディレクトリ: {project_root}

必要に応じて以下のツールを活用してタスクを実行してください：
- GetFilesList：プロジェクト内のファイル一覧を取得する
- ReadFile：ファイルの内容を読む
- MakeNewFile：新しいファイルを作成する
- OverwriteFile：既存ファイルを上書きする
- ExecTest：テストを実行する（言語に応じたテストフレームワークを使用）
- GeneratePullRequestParams：PR作成に必要な情報を生成する
- RecordLgtm：LGTM（レビュー承認）を記録する

## 言語固有の考慮事項
{language_specific_notes}

ユーザーからの指示: 
{instruction}
"""

# エージェントのシステムメッセージ
AGENT_SYSTEM_MESSAGE = """あなたはプロフェッショナルなプログラミングアシスタントです。
ユーザーの指示に基づき、プロジェクト（ルートは {project_root}）の中で、適切なツールを組み合わせて
コーディング、ファイル操作、テスト実行、情報収集などを行い、目的達成を支援してください。

- 実行の前には、まず必要な情報を把握し、ツール選定と段階的な実行を行ってください。
- ディレクトリを指定された場合は、必ずどこにそのディレクトリがあるかを確認してください。
- プロジェクトの言語やフレームワークの慣習に従ってコードを記述してください。
一貫性と再現性のある、正確なコード操作を心がけてください。
"""

# 言語固有の設定テンプレート
LANGUAGE_SPECIFIC_CONFIGS = {
    "python": {
        "test_command": "pytest",
        "package_manager": "pip",
        "config_files": ["requirements.txt", "pyproject.toml", "setup.py"],
        "notes": """
- PEP 8に従ったコーディングスタイルを維持してください
- 型ヒントを適切に使用してください
- docstringを適切に記述してください
- 仮想環境の使用を推奨します
        """,
    },
    "javascript": {
        "test_command": "npm test",
        "package_manager": "npm",
        "config_files": ["package.json", "package-lock.json"],
        "notes": """
- ESLintやPrettierの設定に従ってください
- モジュールシステム（ES6 modules）を適切に使用してください
- 非同期処理にはasync/awaitを使用してください
        """,
    },
    "typescript": {
        "test_command": "npm test",
        "package_manager": "npm",
        "config_files": ["package.json", "tsconfig.json"],
        "notes": """
- TypeScriptの型システムを最大限活用してください
- strictモードを有効にしてください
- インターフェースや型定義を適切に使用してください
        """,
    },
    "java": {
        "test_command": "mvn test",
        "package_manager": "maven",
        "config_files": ["pom.xml", "build.gradle"],
        "notes": """
- Javaの命名規則に従ってください
- 適切な例外処理を実装してください
- JavaDocコメントを記述してください
        """,
    },
    "go": {
        "test_command": "go test",
        "package_manager": "go mod",
        "config_files": ["go.mod", "go.sum"],
        "notes": """
- gofmtでフォーマットしてください
- エラーハンドリングを適切に行ってください
- パッケージ構造を適切に設計してください
        """,
    },
    "rust": {
        "test_command": "cargo test",
        "package_manager": "cargo",
        "config_files": ["Cargo.toml", "Cargo.lock"],
        "notes": """
- Rustの所有権システムを理解して使用してください
- cargo fmtでフォーマットしてください
- エラーハンドリングにResult型を使用してください
        """,
    },
    "terraform": {
        "test_command": "terraform plan",
        "package_manager": "terraform",
        "config_files": ["main.tf", "variables.tf", "outputs.tf"],
        "notes": """
- Terraformのベストプラクティスに従ってください
- 変数とアウトプットを適切に定義してください
- リソースの命名規則を統一してください
        """,
    },
}


def get_language_config(language: str) -> dict:
    """
    指定された言語の設定を取得する

    Args:
        language: プログラミング言語

    Returns:
        言語固有の設定辞書
    """
    return LANGUAGE_SPECIFIC_CONFIGS.get(language.lower(), {})
