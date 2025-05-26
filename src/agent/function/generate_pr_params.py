from src.agent.schema.generate_pr_params_input import GeneratePRParamsInput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.function.base import BaseFunction
from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool


class GeneratePullRequestParamsFunction(BaseFunction):
    """PRのタイトルと説明を生成するFunction"""

    @staticmethod
    def execute(
        instruction: str,
        programmer_output: str,
        diff: str = "",
    ) -> dict[str, str]:
        """PRのタイトルと説明を生成する

        Args:
            instruction (str): プログラマーへの指示内容
            programmer_output (str): プログラマーの出力
            diff (str, optional): コードの差分. デフォルトは空文字.

        Returns:
            Dict[str, str]: PRタイトルと説明
        """
        try:
            # LLMクライアントの初期化
            llm_client = AzureOpenAIClient()
            chat_llm = llm_client.initialize_chat()

            # PRタイトルの生成
            title_prompt = PromptTemplate.from_template(
                """
あなたはプルリクエストのタイトル作成の専門家です。
以下の指示内容から、適切なプルリクエストのタイトルを生成してください。

タイトルのルール:
1. 簡潔で明確に変更内容を表現する
2. 英語で記述する
3. 先頭に適切な接頭語を付ける（例: feat:, fix:, refactor:, docs:, chore:, test:）
4. 最大80文字以内にする
5. 命令形で書く（例: "Add user authentication"）

プログラマーへの指示:
{instruction}

プログラマーの出力:
{programmer_output}

出力する形式:
タイトルのみを出力してください。説明や前後のテキストは不要です。
                """,
            )

            title_message = [
                HumanMessage(
                    content=title_prompt.format(
                        instruction=instruction, 
                        programmer_output=programmer_output[:500] if programmer_output else "出力なし"
                    )
                )
            ]
            title_result = chat_llm.invoke(title_message)
            pr_title = title_result.content.strip()

            # PR説明文の生成
            description_prompt = PromptTemplate.from_template(
                """
あなたはプルリクエストの説明文作成の専門家です。
以下の情報から、詳細で分かりやすいプルリクエストの説明文を生成してください。

説明文のルール:
1. マークダウン形式で記述する
2. 以下のセクションを含める:
   - 概要: 変更内容の簡潔な説明
   - 詳細: 実装方法や特筆すべき点
   - テスト方法: 変更の検証方法（あれば）
3. 簡潔かつ詳細に記述する

プログラマーへの指示:
{instruction}

プログラマーの出力:
{programmer_output}

コードの差分:
{diff}

出力する形式:
マークダウン形式の説明文を出力してください。
                """,
            )

            description_message = [
                HumanMessage(
                    content=description_prompt.format(
                        instruction=instruction,
                        programmer_output=programmer_output[:500] if programmer_output else "出力なし",
                        diff=diff[:1000] if diff else "差分なし"
                    )
                )
            ]
            description_result = chat_llm.invoke(description_message)
            pr_description = description_result.content.strip()

            return {
                "result": "success",
                "pr_title": pr_title,
                "pr_description": pr_description,
            }

        except Exception as e:
            return {
                "result": "error",
                "message": f"PRパラメータ生成に失敗しました: {str(e)}",
                "error": str(e),
            }

    @classmethod
    def to_tool(cls: type["GeneratePullRequestParamsFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="プルリクエストのタイトルと説明文を生成します。",
            func=cls.execute,
            args_schema=GeneratePRParamsInput,
        ) 