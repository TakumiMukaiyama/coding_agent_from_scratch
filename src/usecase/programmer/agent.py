from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import BaseTool

from src.agent.function.create_branch import CreateBranchFunction
from src.agent.function.exec_rspec_test import ExecRspecTestFunction
from src.agent.function.generate_diff import GenerateDiffFunction
from src.agent.function.generate_pull_request_params import (
    GeneratePullRequestParamsFunction,
)
from src.agent.function.get_files_list import GetFilesListFunction
from src.agent.function.google_search import GoogleSearchFunction
from src.agent.function.make_new_file import MakeNewFileFunction
from src.agent.function.open_url import OpenUrlFunction
from src.agent.function.over_write_file import OverwriteFileFunction
from src.agent.function.read_file import ReadFileFunction
from src.agent.schema.programmer_input import ProgrammerInput
from src.agent.schema.programmer_output import ProgrammerOutput
from src.application.chain.pydantic_chain import PydanticChain
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.dependency.chaindependency import ChainDependency
from src.infrastructure.config.prompt import (
    PROGRAMMER_AGENT_SYSTEM_MESSAGE,
    PROGRAMMER_PROMPT_TEMPLATE,
    get_language_config,
)


class ProgrammerAgent:
    def __init__(self, default_project_root: str = "src/"):
        self.llm_client = AzureOpenAIClient()
        self.chat_llm = self.llm_client.initialize_chat()
        self.default_project_root = default_project_root

        self.chain = self._initialize_chain()
        self.tools = self._initialize_tools()

        self.agent_executor: AgentExecutor = self._initialize_executor(
            default_project_root
        )

    def _initialize_chain(self) -> PydanticChain:
        return PydanticChain(
            chat_llm=self.chat_llm,
            chain_dependency=ChainDependency(
                prompt_template=PROGRAMMER_PROMPT_TEMPLATE,
                input_schema=ProgrammerInput,
                output_schema=ProgrammerOutput,
            ),
        )

    def _initialize_tools(self) -> list[BaseTool]:
        return [
            GetFilesListFunction.to_tool(),
            ReadFileFunction.to_tool(),
            OverwriteFileFunction.to_tool(),
            MakeNewFileFunction.to_tool(),
            ExecRspecTestFunction.to_tool(),
            GoogleSearchFunction.to_tool(),
            OpenUrlFunction.to_tool(),
            GeneratePullRequestParamsFunction.to_tool(),
            CreateBranchFunction.to_tool(),
            GenerateDiffFunction.to_tool(),
        ]

    def _initialize_executor(self, project_root: str) -> AgentExecutor:
        # Generate system message according to project root
        system_message = PROGRAMMER_AGENT_SYSTEM_MESSAGE.format(project_root=project_root)

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        agent = create_openai_tools_agent(
            llm=self.chat_llm,
            tools=self.tools,
            prompt=prompt,
        )
        return AgentExecutor(
            agent=agent, tools=self.tools, max_iterations=30, verbose=True
        )

    def _prepare_input(self, programmer_input: ProgrammerInput) -> ProgrammerInput:
        """
        Preprocess input and automatically generate language-specific notes

        Args:
            programmer_input: Original input

        Returns:
            Preprocessed input
        """
        # If language-specific notes are empty, automatically generate them
        if not programmer_input.language_specific_notes:
            language_config = get_language_config(programmer_input.language)
            programmer_input.language_specific_notes = language_config.get("notes", "")

        return programmer_input

    def execute(self, programmer_input: ProgrammerInput):
        """
        Execute the programmer agent

        Args:
            programmer_input: Input to the programmer

        Returns:
            Execution result
        """
        # Preprocess input
        processed_input = self._prepare_input(programmer_input)

        # Reinitialize agent if project root has changed
        if processed_input.project_root != self.default_project_root:
            self.agent_executor = self._initialize_executor(
                processed_input.project_root
            )
            self.default_project_root = processed_input.project_root

        # Execute agent
        return self.agent_executor.invoke({"input": processed_input.instruction})

    def run(self, instruction: str, reviewer_comment: str | None = None) -> str:
        """Execute the programmer agent.

        Args:
            instruction (str): Instruction to the programmer
            reviewer_comment (str | None): Feedback from review

        Returns:
            str: Programmer's output
        """
        if reviewer_comment:
            input_text = (
                f"{instruction}\n\n[Feedback from Reviewer]:\n{reviewer_comment}"
            )
        else:
            input_text = instruction

        result = self.agent_executor.invoke({"input": input_text})
        return result["output"]

    def get_diff(
        self,
        base_branch: str | None = None,
        target_branch: str | None = None,
        file_path: str | None = None,
    ) -> str:
        """Get diff for current changes.

        Args:
            base_branch (str, optional): Source branch name for comparison. Defaults to None.
            target_branch (str | None, optional): Target branch name for comparison. Defaults to None (current branch).

        Returns:
            str: Generated diff
        """
        diff_function = GenerateDiffFunction()
        result = diff_function.execute(
            base_branch=base_branch, target_branch=target_branch, file_path=file_path
        )

        if result["result"] == "error":
            return f"Diff retrieval error: {result['message']}"

        return result["diff"]
