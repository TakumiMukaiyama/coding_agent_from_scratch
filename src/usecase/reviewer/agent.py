from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import BaseTool

from src.agent.function.record_lgtm import RecordLgtmFunction
from src.agent.function.review_code_function import ReviewCodeFunction
from src.agent.schema.reviewer_input import ReviewerInput
from src.agent.schema.reviewer_output import ReviewerOutput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.infrastructure.config.prompt import REVIEWER_PROMPT, get_language_config


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

    def _initialize_tools(self) -> list[BaseTool]:
        return [
            ReviewCodeFunction.to_tool(),
            RecordLgtmFunction.to_tool(),
        ]

    def _get_language_specific_prompt(self, language: str | None) -> str:
        """言語固有のレビューノートを取得する.

        Args:
            language: プログラミング言語

        Returns:
            言語固有のレビューノート
        """
        if not language:
            return "一般的なコーディングベストプラクティスに従ってレビューしてください。"

        config = get_language_config(language)
        return config.get("review_notes", "一般的なコーディングベストプラクティスに従ってレビューしてください。")

    def _initialize_executor(self, language: str | None = None) -> AgentExecutor:
        """エージェントエグゼキューターを初期化する.

        Args:
            language: プログラミング言語

        Returns:
            AgentExecutor
        """
        language_specific_notes = self._get_language_specific_prompt(language)
        system_content = REVIEWER_PROMPT.format(language_specific_review_notes=language_specific_notes)

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_content),
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
        return AgentExecutor(agent=agent, tools=self.tools, max_iterations=30, verbose=True)

    def run(self, reviewer_input: ReviewerInput) -> ReviewerOutput:
        """コードレビューを実行する.

        Args:
            reviewer_input (ReviewerInput): レビュー入力

        Returns:
            ReviewerOutput: レビュー出力
        """
        # LGTM状態をリセット
        RecordLgtmFunction.reset_lgtm()

        # 言語に応じてエージェントエグゼキューターを初期化
        self.agent_executor = self._initialize_executor(reviewer_input.language)

        input_text = f"""
            コードレビューを行ってください。
            
            差分:
            {reviewer_input.diff}
            
            """
        if reviewer_input.programmer_comment:
            input_text += f"\n\nプログラマーからのコメント:\n{reviewer_input.programmer_comment}"

        if reviewer_input.language:
            input_text += f"\n\nプログラミング言語: {reviewer_input.language}"

        if reviewer_input.project_type:
            input_text += f"\nプロジェクトタイプ: {reviewer_input.project_type}"

        agent_result = self.agent_executor.invoke({"input": input_text})
        output_text = agent_result["output"]

        if isinstance(output_text, dict) and "review_result" in output_text:
            summary = output_text["review_result"]
        else:
            summary = str(output_text)

        lgtm_flag = RecordLgtmFunction.lgtm()

        return ReviewerOutput(
            summary=summary,
            suggestions=[],  # あとでstructured出力できる
            lgtm=lgtm_flag,
        )
