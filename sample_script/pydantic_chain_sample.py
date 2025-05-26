"""
Pydanticを使用したLangChainのサンプルスクリプト

このスクリプトは、PydanticChainを使用して簡単な質問応答システムを実装します。
入力として質問を受け取り、LLMを使って回答を生成します。
"""

from pydantic import Field

from src.application.chain.pydantic_chain import PydanticChain
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.infrastructure.config.agent_setting import agent_settings
from src.application.dependency.chaindependency import ChainDependency
from src.application.schema.base import BaseInput, BaseOutput


class QuestionInput(BaseInput):
    """質問入力スキーマ"""

    question: str = Field(description="ユーザーからの質問")


class AnswerOutput(BaseOutput):
    """回答出力スキーマ"""

    answer: str = Field(description="質問に対する回答")
    confidence: float = Field(description="回答の確信度（0.0から1.0の値）")


# プロンプトテンプレートの定義
PROMPT_TEMPLATE = """
以下の質問に答えてください。
質問: {question}

回答は簡潔かつ正確に行い、回答の確信度も0から1の間の値で示してください。
"""


def main():
    """メイン関数"""
    # LLMクライアントの初期化
    client = AzureOpenAIClient(
        base_url=agent_settings.AZURE_OPENAI_API_ENDPOINT,
        api_key=agent_settings.AZURE_OPENAI_API_KEY,
        deployment_name=agent_settings.AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O,
        embedding_model=agent_settings.AZURE_OPENAI_EMBEDDING_MODEL,
    )

    # 依存関係の設定
    chain_dependency = ChainDependency(
        prompt_template=PROMPT_TEMPLATE,
        input_schema=QuestionInput,
        output_schema=AnswerOutput,
    )

    # PydanticChainの初期化
    chain = PydanticChain(
        chat_llm=client.initialize_chat(),
        chain_dependency=chain_dependency,
    )

    # 入力の作成
    question_input = QuestionInput(question="人工知能とは何ですか？")

    # チェーンの実行
    try:
        # プロンプトの確認
        prompt = chain.get_prompt(question_input)
        print(f"使用されるプロンプト:\n{prompt}\n")

        # チェーンの実行
        result = chain.invoke(question_input)
        print(f"回答: {result.answer}")
        print(f"確信度: {result.confidence}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
