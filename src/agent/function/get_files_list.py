import glob
import os
from pathlib import Path
from typing import Dict, List, Set, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.get_files_list_input import GetFilesListInput
from src.application.function.base import BaseFunction

# プロンプト設定ファイルからの言語設定をインポート（オプション）
try:
    from src.infrastructure.config.prompt import get_language_config

    PROMPT_CONFIG_AVAILABLE = True
except ImportError:
    PROMPT_CONFIG_AVAILABLE = False


class GetFilesListFunction(BaseFunction):
    # 言語別のデフォルトファイル拡張子
    DEFAULT_EXTENSIONS_BY_LANGUAGE = {
        "python": ["py", "pyx", "pyi", "ipynb"],
        "javascript": ["js", "jsx", "mjs", "cjs"],
        "typescript": ["ts", "tsx", "d.ts"],
        "java": ["java", "class", "jar"],
        "go": ["go", "mod", "sum"],
        "rust": ["rs", "toml"],
        "c": ["c", "h"],
        "cpp": ["cpp", "cxx", "cc", "hpp", "hxx", "hh"],
        "csharp": ["cs", "csx"],
        "php": ["php", "phtml"],
        "ruby": ["rb", "rake", "gemspec"],
        "swift": ["swift"],
        "kotlin": ["kt", "kts"],
        "scala": ["scala", "sc"],
        "terraform": ["tf", "tfvars", "hcl"],
        "yaml": ["yml", "yaml"],
        "json": ["json", "jsonc"],
        "xml": ["xml", "xsd", "xsl"],
        "html": ["html", "htm", "xhtml"],
        "css": ["css", "scss", "sass", "less"],
        "sql": ["sql", "ddl", "dml"],
        "shell": ["sh", "bash", "zsh", "fish"],
        "powershell": ["ps1", "psm1", "psd1"],
        "docker": ["dockerfile", "dockerignore"],
        "markdown": ["md", "mdx", "markdown"],
        "text": ["txt", "log", "conf", "cfg", "ini"],
    }

    # 一般的な除外パターン
    DEFAULT_EXCLUDE_PATTERNS = [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/venv/**",
        "**/env/**",
        "**/.venv/**",
        "**/.env/**",
        "**/target/**",
        "**/build/**",
        "**/dist/**",
        "**/.git/**",
        "**/.svn/**",
        "**/.hg/**",
        "**/coverage/**",
        "**/.coverage/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.tox/**",
        "**/vendor/**",
        "**/Pods/**",
        "**/.terraform/**",
        "**/terraform.tfstate*",
        "**/*.log",
        "**/*.tmp",
        "**/*.temp",
        "**/.*cache/**",
    ]

    @staticmethod
    def execute(
        file_extensions: List[str] = None,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        root_directory: str = ".",
        max_files: int = 1000,
    ) -> Dict[str, List[str]]:
        """
        指定された条件に基づいてファイル一覧を取得する

        Args:
            file_extensions: 取得するファイルの拡張子リスト
            include_patterns: 含めるファイルパターンのリスト
            exclude_patterns: 除外するファイルパターンのリスト
            root_directory: 検索を開始するルートディレクトリ
            max_files: 取得するファイル数の上限

        Returns:
            ファイル一覧を含む辞書
        """
        # デフォルト設定の適用
        if file_extensions is None and include_patterns is None:
            # デフォルトで一般的なコードファイルを取得
            file_extensions = (
                GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["python"]
                + GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["javascript"]
                + GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["typescript"]
                + GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["markdown"]
                + GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["json"]
                + GetFilesListFunction.DEFAULT_EXTENSIONS_BY_LANGUAGE["yaml"]
            )

        if exclude_patterns is None:
            exclude_patterns = GetFilesListFunction.DEFAULT_EXCLUDE_PATTERNS
        else:
            # ユーザー指定の除外パターンにデフォルトを追加
            exclude_patterns = list(set(exclude_patterns + GetFilesListFunction.DEFAULT_EXCLUDE_PATTERNS))

        # ルートディレクトリの正規化
        root_path = Path(root_directory).resolve()
        if not root_path.exists():
            return {"files_list": [], "error": f"指定されたディレクトリが存在しません: {root_directory}"}

        files_set: Set[str] = set()

        # 現在のディレクトリを変更
        original_cwd = os.getcwd()
        try:
            os.chdir(root_path)

            # include_patternsが指定されている場合
            if include_patterns:
                for pattern in include_patterns:
                    files_set.update(glob.glob(pattern, recursive=True))

            # file_extensionsが指定されている場合
            if file_extensions:
                for ext in file_extensions:
                    # 拡張子から先頭のドットを除去
                    ext = ext.lstrip(".")
                    pattern = f"**/*.{ext}"
                    files_set.update(glob.glob(pattern, recursive=True))

            # 除外パターンの適用
            if exclude_patterns:
                excluded_files = set()
                for pattern in exclude_patterns:
                    excluded_files.update(glob.glob(pattern, recursive=True))
                files_set -= excluded_files

            # ファイルのみをフィルタリング（ディレクトリを除外）
            files_list = [f for f in files_set if os.path.isfile(f)]

            # ファイル数の制限
            if len(files_list) > max_files:
                files_list = files_list[:max_files]
                return {
                    "files_list": sorted(files_list),
                    "warning": f"ファイル数が上限（{max_files}）を超えたため、一部のファイルのみ表示しています。",
                }

            return {"files_list": sorted(files_list)}

        finally:
            os.chdir(original_cwd)

    @classmethod
    def get_extensions_for_language(cls, language: str) -> List[str]:
        """
        指定された言語のデフォルトファイル拡張子を取得する

        Args:
            language: プログラミング言語名

        Returns:
            ファイル拡張子のリスト
        """
        return cls.DEFAULT_EXTENSIONS_BY_LANGUAGE.get(language.lower(), [])

    @classmethod
    def get_all_supported_languages(cls) -> List[str]:
        """
        サポートされている全ての言語のリストを取得する

        Returns:
            サポートされている言語のリスト
        """
        return list(cls.DEFAULT_EXTENSIONS_BY_LANGUAGE.keys())

    @classmethod
    def get_files_for_language(
        cls, language: str, root_directory: str = ".", max_files: int = 1000
    ) -> Dict[str, List[str]]:
        """
        指定された言語のファイルを取得する便利メソッド

        Args:
            language: プログラミング言語名
            root_directory: 検索を開始するルートディレクトリ
            max_files: 取得するファイル数の上限

        Returns:
            ファイル一覧を含む辞書
        """
        extensions = cls.get_extensions_for_language(language)
        if not extensions:
            return {"files_list": [], "error": f"サポートされていない言語です: {language}"}

        # プロンプト設定ファイルから設定ファイルも取得（利用可能な場合）
        if PROMPT_CONFIG_AVAILABLE:
            try:
                config = get_language_config(language)
                config_files = config.get("config_files", [])
                if config_files:
                    # 設定ファイルのパターンを追加
                    include_patterns = [f"**/{cf}" for cf in config_files]
                    return cls.execute(
                        file_extensions=extensions,
                        include_patterns=include_patterns,
                        root_directory=root_directory,
                        max_files=max_files,
                    )
            except Exception:
                pass  # 設定取得に失敗した場合は通常の処理を続行

        return cls.execute(file_extensions=extensions, root_directory=root_directory, max_files=max_files)

    @classmethod
    def to_tool(cls: Type["GetFilesListFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="""プロジェクト配下のファイル一覧を取得します。
            
使用例:
- 全ての一般的なコードファイルを取得: パラメータなし
- Pythonファイルのみ: file_extensions=['py']
- 特定パターン: include_patterns=['src/**/*.js']
- 除外パターン: exclude_patterns=['**/test/**']
- 特定ディレクトリから: root_directory='src/'

サポートされている言語: python, javascript, typescript, java, go, rust, c, cpp, csharp, php, ruby, swift, kotlin, scala, terraform, yaml, json, xml, html, css, sql, shell, powershell, docker, markdown, text
            """,
            func=cls.execute,
            args_schema=GetFilesListInput,
        )


"""
使用例:

# 基本的な使用方法
from src.agent.function.get_files_list import GetFilesListFunction

# 1. 全ての一般的なコードファイルを取得
result = GetFilesListFunction.execute()
print(result["files_list"])

# 2. Pythonファイルのみを取得
result = GetFilesListFunction.execute(file_extensions=["py"])
print(result["files_list"])

# 3. 特定のパターンでファイルを取得
result = GetFilesListFunction.execute(include_patterns=["src/**/*.js", "tests/**/*.py"])
print(result["files_list"])

# 4. 除外パターンを指定
result = GetFilesListFunction.execute(
    file_extensions=["py"],
    exclude_patterns=["**/test/**", "**/migrations/**"]
)
print(result["files_list"])

# 5. 特定のディレクトリから検索
result = GetFilesListFunction.execute(
    file_extensions=["ts", "tsx"],
    root_directory="frontend/src"
)
print(result["files_list"])

# 6. 言語固有のファイルを取得（便利メソッド）
result = GetFilesListFunction.get_files_for_language("python")
print(result["files_list"])

# 7. サポートされている言語の一覧を取得
languages = GetFilesListFunction.get_all_supported_languages()
print(languages)

# 8. 特定言語の拡張子を取得
extensions = GetFilesListFunction.get_extensions_for_language("typescript")
print(extensions)  # ['ts', 'tsx', 'd.ts']
"""
