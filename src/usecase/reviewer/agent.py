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
from src.infrastructure.config.prompt import REVIEWER_AGENT_SYSTEM_MESSAGE
from src.infrastructure.utils.logger import get_logger


class ReviewerAgent:
    """Agent that performs code reviews."""

    def __init__(self) -> None:
        """Constructor.

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
                    content=REVIEWER_AGENT_SYSTEM_MESSAGE
                ),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        # Use create_openai_tools_agent for compatibility with o3-mini model
        agent = create_openai_tools_agent(
            llm=self.chat_llm,
            tools=self.tools,
            prompt=prompt,
        )
        return AgentExecutor(agent=agent, tools=self.tools, max_iterations=30, verbose=True)

    def run(self, reviewer_input: ReviewerInput) -> ReviewerOutput:
        """Execute code review.

        Args:
            reviewer_input (ReviewerInput): Review input

        Returns:
            ReviewerOutput: Review output
        """
        # Reset LGTM status
        RecordLgtmFunction.reset_lgtm()
        input_text = f"""
            Please perform a code review.
            Review in detail from the perspectives of code quality, security, and best practices,
            and point out specific issues or improvements if any.
            
            After review completion:
            - If the code has no issues and can be approved: Please call the record_lgtm_function tool
            - If there are issues: Please point out specific improvements
            
            Diff:
            {reviewer_input.diff}
            
            """
        if reviewer_input.programmer_comment:
            input_text += f"\n\nComment from programmer:\n{reviewer_input.programmer_comment}"

        agent_result = self.agent_executor.invoke({"input": input_text})
        output_text = agent_result["output"]

        if isinstance(output_text, dict) and "review_result" in output_text:
            summary = output_text["review_result"]
        else:
            summary = str(output_text)

        lgtm_flag = RecordLgtmFunction.lgtm()

        # Debug logs
        logger = get_logger(__name__)
        logger.info(f"Review completed - LGTM status: {lgtm_flag}")
        if lgtm_flag:
            logger.info("LGTM tool was called successfully")
        else:
            logger.warning("LGTM tool was not called")

        return ReviewerOutput(
            summary=summary,
            suggestions=[],  # Can be structured output later
            lgtm=lgtm_flag,
        )
