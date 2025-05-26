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

# レビュワーエージェントのプロンプトテンプレート
REVIEWER_PROMPT = """あなたはプロフェッショナルなコードレビュワーです。
提供されたコード差分を精査し、以下の観点から問題点や改善点を指摘してください。

## レビュー観点
- コードの品質と可読性
- セキュリティ上の問題
- パフォーマンスの問題
- ベストプラクティスの遵守
- バグの可能性
- テストの必要性

## 言語固有の考慮事項
{language_specific_review_notes}

## レビュー指針
- 建設的で具体的なフィードバックを提供してください
- 問題がある場合は、具体的な修正案を提示してください
- コードが適切な場合は、LGTM (Looks Good To Me) を記録してください
- 重大な問題がある場合は、修正を求めてください

適切なレビューを行い、必要に応じてLGTMを記録してください。"""

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
        "review_notes": """
- PEP 8スタイルガイドの遵守を確認
- 型ヒントの適切な使用
- docstringの品質と完全性
- セキュリティ脆弱性（SQLインジェクション、XSSなど）
- パフォーマンス（リスト内包表記、ジェネレータの使用）
- 例外処理の適切性
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
        "review_notes": """
- ESLintルールの遵守
- ES6+の機能の適切な使用
- 非同期処理のベストプラクティス
- セキュリティ（XSS、CSRF対策）
- パフォーマンス（メモリリーク、DOM操作の最適化）
- エラーハンドリングの適切性
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
        "review_notes": """
- 型安全性の確保
- strictモードの活用
- インターフェースと型定義の適切性
- ジェネリクスの効果的な使用
- any型の使用を最小限に抑制
- 型ガードの適切な実装
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
        "review_notes": """
- Javaコーディング規約の遵守
- オブジェクト指向設計の原則
- 例外処理の適切性
- メモリ管理とリソース管理
- セキュリティ（入力検証、認証・認可）
- パフォーマンス（コレクションの選択、ストリームAPI）
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
        "review_notes": """
- Goの慣用的な書き方（idioms）
- エラーハンドリングの適切性
- ゴルーチンとチャネルの安全な使用
- メモリ効率とガベージコレクション
- パッケージ設計とインターフェース
- 並行処理の安全性
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
        "review_notes": """
- 所有権とライフタイムの適切な管理
- メモリ安全性の確保
- エラーハンドリング（Result型、Option型）
- パフォーマンス（ゼロコスト抽象化）
- 並行処理の安全性
- unsafe コードの適切な使用
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
        "review_notes": """
- Terraformのベストプラクティス遵守
- リソースの命名規則と構造
- 変数とアウトプットの適切な定義
- セキュリティ設定（IAM、ネットワーク）
- 状態管理とバックエンド設定
- モジュール化と再利用性
- 特定の環境（snowflake/environments/配下）に差分がない場合の対応
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
