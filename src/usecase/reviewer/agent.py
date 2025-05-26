from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import BaseTool

from src.infrastructure.utils.logger import get_logger
from src.agent.function.record_lgtm import RecordLgtmFunction
from src.agent.function.review_code_function import ReviewCodeFunction
from src.agent.schema.reviewer_input import ReviewerInput
from src.agent.schema.reviewer_output import ReviewerOutput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient


class ReviewerAgent:
    """コードレビューを実行するエージェント."""

    def __init__(self) -> None:
        """コンストラクタ.

        Args:
            llm_client (AzureOpenAIClient): AzureOpenAIClient
        """
        self.llm_client = AzureOpenAIClient()
        self.chat_llm = self.llm_client.initialize_chat()
        self.tools = self._initialize_tools()
        self.agent_executor = self._initialize_executor()

    def _initialize_tools(self) -> list[BaseTool]:
        return [
            ReviewCodeFunction.to_tool(),
            RecordLgtmFunction.to_tool(),
        ]

    def _initialize_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""あなたはプロフェッショナルなレビュワーです。
コード差分を精査し、問題点や改善点を指摘してください。
以下の観点でレビューを行ってください：
- コードの品質（可読性、保守性、パフォーマンス）
- セキュリティ上の問題
- ベストプラクティスの遵守
- バグの可能性
- 設計上の問題

重要：レビューの結果、コードに問題がなく承認できる場合は、必ずrecord_lgtm_functionツールを呼び出してLGTM (Looks Good To Me) を記録してください。
問題がある場合は、具体的な改善点を指摘してください。""",
                ),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        # o3-miniモデルとの互換性のために、create_openai_tools_agentを使用
        agent = create_openai_tools_agent(
            llm=self.chat_llm,
            tools=self.tools,
            prompt=prompt,
        )
        return AgentExecutor(
            agent=agent, tools=self.tools, max_iterations=30, verbose=True
        )

    def run(self, reviewer_input: ReviewerInput) -> ReviewerOutput:
        """コードレビューを実行する.

        Args:
            reviewer_input (ReviewerInput): レビュー入力

        Returns:
            ReviewerOutput: レビュー出力
        """
        # LGTM状態をリセット
        RecordLgtmFunction.reset_lgtm()
        input_text = f"""
            コードレビューを行ってください。
            コードの品質、セキュリティ、ベストプラクティスの観点から詳細にレビューし、
            問題点や改善点があれば具体的に指摘してください。
            
            レビュー完了後：
            - コードに問題がなく承認できる場合：必ずrecord_lgtm_functionツールを呼び出してください
            - 問題がある場合：具体的な改善点を指摘してください
            
            差分:
            {reviewer_input.diff}
            
            """
        if reviewer_input.programmer_comment:
            input_text += (
                f"\n\nプログラマーからのコメント:\n{reviewer_input.programmer_comment}"
            )

        agent_result = self.agent_executor.invoke({"input": input_text})
        output_text = agent_result["output"]

        if isinstance(output_text, dict) and "review_result" in output_text:
            summary = output_text["review_result"]
        else:
            summary = str(output_text)

        lgtm_flag = RecordLgtmFunction.lgtm()

        # デバッグ用ログ

        logger = get_logger(__name__)
        logger.info(f"レビュー完了 - LGTM状態: {lgtm_flag}")
        if lgtm_flag:
            logger.info("LGTMツールが正常に呼び出されました")
        else:
            logger.warning("LGTMツールが呼び出されていません")

        return ReviewerOutput(
            summary=summary,
            suggestions=[],  # あとでstructured出力できる
            lgtm=lgtm_flag,
        )
