import glob
import os
from pathlib import Path
from typing import Dict, List, Set, Type

from langchain_core.tools import StructuredTool

from src.agent.schema.get_files_list_input import GetFilesListInput
from src.application.function.base import BaseFunction

# Import language settings from prompt configuration file (optional)
try:
    from src.infrastructure.config.prompt import get_language_config

    PROMPT_CONFIG_AVAILABLE = True
except ImportError:
    PROMPT_CONFIG_AVAILABLE = False


class GetFilesListFunction(BaseFunction):
    # Default file extensions by language
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

    # Common exclude patterns
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
        Get file list based on specified conditions

        Args:
            file_extensions: List of file extensions to retrieve
            include_patterns: List of file patterns to include
            exclude_patterns: List of file patterns to exclude
            root_directory: Root directory to start search from
            max_files: Maximum number of files to retrieve

        Returns:
            Dictionary containing file list
        """
        # Apply default settings
        if file_extensions is None and include_patterns is None:
            # Get common code files by default
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
            # Add default patterns to user-specified exclude patterns
            exclude_patterns = list(
                set(exclude_patterns + GetFilesListFunction.DEFAULT_EXCLUDE_PATTERNS)
            )

        # Normalize root directory
        root_path = Path(root_directory).resolve()
        if not root_path.exists():
            return {
                "files_list": [],
                "error": f"Specified directory does not exist: {root_directory}",
            }

        files_set: Set[str] = set()

        # Change current directory
        original_cwd = os.getcwd()
        try:
            os.chdir(root_path)

            # If include_patterns is specified
            if include_patterns:
                for pattern in include_patterns:
                    files_set.update(glob.glob(pattern, recursive=True))

            # If file_extensions is specified
            if file_extensions:
                for ext in file_extensions:
                    # Remove leading dot from extension
                    ext = ext.lstrip(".")
                    pattern = f"**/*.{ext}"
                    files_set.update(glob.glob(pattern, recursive=True))

            # Apply exclude patterns
            if exclude_patterns:
                excluded_files = set()
                for pattern in exclude_patterns:
                    excluded_files.update(glob.glob(pattern, recursive=True))
                files_set -= excluded_files

            # Filter files only (exclude directories)
            files_list = [f for f in files_set if os.path.isfile(f)]

            # Limit number of files
            if len(files_list) > max_files:
                files_list = files_list[:max_files]
                return {
                    "files_list": sorted(files_list),
                    "warning": f"Number of files exceeded the limit ({max_files}), showing only some files.",
                }

            return {"files_list": sorted(files_list)}

        finally:
            os.chdir(original_cwd)

    @classmethod
    def get_extensions_for_language(cls, language: str) -> List[str]:
        """
        Get default file extensions for the specified language

        Args:
            language: Programming language name

        Returns:
            List of file extensions
        """
        return cls.DEFAULT_EXTENSIONS_BY_LANGUAGE.get(language.lower(), [])

    @classmethod
    def get_all_supported_languages(cls) -> List[str]:
        """
        Get list of all supported languages

        Returns:
            List of supported languages
        """
        return list(cls.DEFAULT_EXTENSIONS_BY_LANGUAGE.keys())

    @classmethod
    def get_files_for_language(
        cls, language: str, root_directory: str = ".", max_files: int = 1000
    ) -> Dict[str, List[str]]:
        """
        Convenience method to get files for the specified language

        Args:
            language: Programming language name
            root_directory: Root directory to start search from
            max_files: Maximum number of files to retrieve

        Returns:
            Dictionary containing file list
        """
        extensions = cls.get_extensions_for_language(language)
        if not extensions:
            return {
                "files_list": [],
                "error": f"Unsupported language: {language}",
            }

        # Also get config files from prompt config file (if available)
        if PROMPT_CONFIG_AVAILABLE:
            try:
                config = get_language_config(language)
                config_files = config.get("config_files", [])
                if config_files:
                    # Add config file patterns
                    include_patterns = [f"**/{cf}" for cf in config_files]
                    return cls.execute(
                        file_extensions=extensions,
                        include_patterns=include_patterns,
                        root_directory=root_directory,
                        max_files=max_files,
                    )
            except Exception:
                pass  # Continue with normal processing if config retrieval fails

        return cls.execute(
            file_extensions=extensions,
            root_directory=root_directory,
            max_files=max_files,
        )

    @classmethod
    def to_tool(cls: Type["GetFilesListFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="""Get file list under the project.
            
Usage examples:
- Get all common code files: no parameters
- Python files only: file_extensions=['py']
- Specific patterns: include_patterns=['src/**/*.js']
- Exclude patterns: exclude_patterns=['**/test/**']
- From specific directory: root_directory='src/'

Supported languages: python, javascript, typescript, java, go, rust, c, cpp, csharp, php, ruby, swift, kotlin, scala, terraform, yaml, json, xml, html, css, sql, shell, powershell, docker, markdown, text
            """,
            func=cls.execute,
            args_schema=GetFilesListInput,
        )


"""
Usage examples:

# Basic usage
from src.agent.function.get_files_list import GetFilesListFunction

# 1. Get all common code files
result = GetFilesListFunction.execute()
print(result["files_list"])

# 2. Get Python files only
result = GetFilesListFunction.execute(file_extensions=["py"])
print(result["files_list"])

# 3. Get files with specific patterns
result = GetFilesListFunction.execute(include_patterns=["src/**/*.js", "tests/**/*.py"])
print(result["files_list"])

# 4. Specify exclude patterns
result = GetFilesListFunction.execute(
    file_extensions=["py"],
    exclude_patterns=["**/test/**", "**/migrations/**"]
)
print(result["files_list"])

# 5. Search from specific directory
result = GetFilesListFunction.execute(
    file_extensions=["ts", "tsx"],
    root_directory="frontend/src"
)
print(result["files_list"])

# 6. Get language-specific files (convenience method)
result = GetFilesListFunction.get_files_for_language("python")
print(result["files_list"])

# 7. Get list of supported languages
languages = GetFilesListFunction.get_all_supported_languages()
print(languages)

# 8. Get extensions for specific language
extensions = GetFilesListFunction.get_extensions_for_language("typescript")
print(extensions)  # ['ts', 'tsx', 'd.ts']
"""
