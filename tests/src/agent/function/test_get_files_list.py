"""
Unit test for GetFilesListFunction
"""

from unittest.mock import patch

import pytest

from src.agent.function.get_files_list import GetFilesListFunction
from src.agent.schema.get_files_list_input import GetFilesListInput


class TestGetFilesListFunction:
    @patch("src.agent.function.get_files_list.glob.glob")
    @patch("src.agent.function.get_files_list.os.path.isfile")
    def test_execute(self, mock_isfile, mock_glob):
        """Test for execute method"""
        # Set up mock
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

        # Make all files treated as actual files
        mock_isfile.return_value = True

        # Test execution
        result = GetFilesListFunction.execute()

        # Verification
        assert "files_list" in result
        assert isinstance(result["files_list"], list)
        # Check that multiple language files are included by default
        assert len(result["files_list"]) > 0

    @patch("src.agent.function.get_files_list.glob.glob")
    @patch("src.agent.function.get_files_list.os.path.isfile")
    def test_execute_with_specific_extensions(self, mock_isfile, mock_glob):
        """Test for specific extensions"""
        # Set up mock
        mock_glob.side_effect = lambda pattern, recursive: {
            "**/*.py": ["config.py", "dir/settings.py"],
        }.get(pattern, [])

        mock_isfile.return_value = True

        # Test execution
        result = GetFilesListFunction.execute(file_extensions=["py"])

        # Verification
        assert "files_list" in result
        assert len(result["files_list"]) == 2
        assert "config.py" in result["files_list"]
        assert "dir/settings.py" in result["files_list"]

    def test_get_extensions_for_language(self):
        """Test for getting extensions for language"""
        # Python
        python_extensions = GetFilesListFunction.get_extensions_for_language("python")
        assert "py" in python_extensions
        assert "pyx" in python_extensions

        # TypeScript
        ts_extensions = GetFilesListFunction.get_extensions_for_language("typescript")
        assert "ts" in ts_extensions
        assert "tsx" in ts_extensions

        # Unknown language
        unknown_extensions = GetFilesListFunction.get_extensions_for_language("unknown")
        assert unknown_extensions == []

    def test_get_all_supported_languages(self):
        """Test for getting all supported languages"""
        languages = GetFilesListFunction.get_all_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert isinstance(languages, list)

    @patch("src.agent.function.get_files_list.StructuredTool.from_function")
    def test_to_tool(self, mock_from_function):
        """Test for to_tool method"""
        # Set up mock
        mock_from_function.return_value = "mock_tool"

        # Test execution
        with patch.object(
            GetFilesListFunction,
            "function_name",
            return_value="get_files_list_function",
        ):
            result = GetFilesListFunction.to_tool()

        # Verification - Update to new description
        mock_from_function.assert_called_once()
        call_args = mock_from_function.call_args
        assert call_args[1]["name"] == "get_files_list_function"
        assert "Get the list of files under the project" in call_args[1]["description"]
        assert call_args[1]["func"] == GetFilesListFunction.execute
        assert call_args[1]["args_schema"] == GetFilesListInput
        assert result == "mock_tool"


if __name__ == "__main__":
    pytest.main()
