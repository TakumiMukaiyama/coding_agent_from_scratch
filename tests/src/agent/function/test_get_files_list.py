"""
GetFilesListFunctionの単体テスト
"""

from unittest.mock import patch

import pytest

from src.agent.function.get_files_list import GetFilesListFunction
from src.agent.schema.get_files_list_input import GetFilesListInput


class TestGetFilesListFunction:
    @patch("src.agent.function.get_files_list.glob.glob")
    @patch("src.agent.function.get_files_list.os.path.isfile")
    def test_execute(self, mock_isfile, mock_glob):
        """execute メソッドのテスト"""
        # モックの設定
        mock_glob.side_effect = lambda pattern, recursive: {
            "**/*.py": ["config.py", "dir/settings.py"],
            "**/*.pyx": ["module.pyx"],
            "**/*.pyi": ["types.pyi"],
            "**/*.ipynb": ["notebook.ipynb"],
            "**/*.js": ["script.js"],
            "**/*.jsx": ["component.jsx"],
            "**/*.mjs": ["module.mjs"],
            "**/*.cjs": ["common.cjs"],
            "**/*.ts": ["app.ts"],
            "**/*.tsx": ["component.tsx"],
            "**/*.d.ts": ["types.d.ts"],
            "**/*.md": ["README.md"],
            "**/*.mdx": ["doc.mdx"],
            "**/*.markdown": ["guide.markdown"],
            "**/*.json": ["package.json"],
            "**/*.jsonc": ["config.jsonc"],
            "**/*.yml": ["config.yml"],
            "**/*.yaml": ["docker-compose.yaml"],
        }.get(pattern, [])

        # 全てのファイルが実際のファイルとして扱われるようにする
        mock_isfile.return_value = True

        # テスト実行
        result = GetFilesListFunction.execute()

        # 検証
        assert "files_list" in result
        assert isinstance(result["files_list"], list)
        # デフォルトでは複数の言語のファイルが含まれることを確認
        assert len(result["files_list"]) > 0

    @patch("src.agent.function.get_files_list.glob.glob")
    @patch("src.agent.function.get_files_list.os.path.isfile")
    def test_execute_with_specific_extensions(self, mock_isfile, mock_glob):
        """特定の拡張子でのテスト"""
        # モックの設定
        mock_glob.side_effect = lambda pattern, recursive: {
            "**/*.py": ["config.py", "dir/settings.py"],
        }.get(pattern, [])

        mock_isfile.return_value = True

        # テスト実行
        result = GetFilesListFunction.execute(file_extensions=["py"])

        # 検証
        assert "files_list" in result
        assert len(result["files_list"]) == 2
        assert "config.py" in result["files_list"]
        assert "dir/settings.py" in result["files_list"]

    def test_get_extensions_for_language(self):
        """言語別拡張子取得のテスト"""
        # Python
        python_extensions = GetFilesListFunction.get_extensions_for_language("python")
        assert "py" in python_extensions
        assert "pyx" in python_extensions

        # TypeScript
        ts_extensions = GetFilesListFunction.get_extensions_for_language("typescript")
        assert "ts" in ts_extensions
        assert "tsx" in ts_extensions

        # 存在しない言語
        unknown_extensions = GetFilesListFunction.get_extensions_for_language("unknown")
        assert unknown_extensions == []

    def test_get_all_supported_languages(self):
        """サポート言語一覧取得のテスト"""
        languages = GetFilesListFunction.get_all_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert isinstance(languages, list)

    @patch("src.agent.function.get_files_list.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """to_tool メソッドのテスト"""
        # モックの設定
        mock_from_function.return_value = "mock_tool"

        # テスト実行
        with patch.object(
            GetFilesListFunction,
            "function_name",
            return_value="get_files_list_function",
        ):
            result = GetFilesListFunction.to_tool()

        # 検証 - 新しい説明文に合わせて更新
        mock_from_function.assert_called_once()
        call_args = mock_from_function.call_args
        assert call_args[1]["name"] == "get_files_list_function"
        assert (
            "プロジェクト配下のファイル一覧を取得します" in call_args[1]["description"]
        )
        assert call_args[1]["func"] == GetFilesListFunction.execute
        assert call_args[1]["args_schema"] == GetFilesListInput
        assert result == "mock_tool"


if __name__ == "__main__":
    pytest.main()
