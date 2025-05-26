import os
import subprocess

from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate

from src.agent.schema.reviewer_input import ReviewerInput
from src.agent.schema.reviewer_output import ReviewerOutput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.infrastructure.utils.logger import get_logger
from src.usecase.programmer.agent import ProgrammerAgent
from src.usecase.reviewer.agent import ReviewerAgent

logger = get_logger(__name__)


class AgentCoordinator:
    """Coordinator that manages collaboration between ProgrammerAgent and ReviewerAgent."""

    def __init__(self):
        """Constructor."""
        self.programmer_agent = ProgrammerAgent()
        self.reviewer_agent = ReviewerAgent()
        self.base_branch = "main"
        self.working_branch = None
        self.llm_client = AzureOpenAIClient()
        self.chat_llm = self.llm_client.initialize_chat()
        self.repo_path = os.getcwd()  # Use current directory as repository path
        self.repo_full_name = "coding_agent_from_scratch"

    def generate_branch_name(self, instruction: str) -> str:
        """Generate Git branch name from instruction content.

        Args:
            instruction (str): Instruction to the programmer

        Returns:
            str: Generated branch name
        """
        prompt = PromptTemplate.from_template(
            """
You are a Git branch naming expert.
Please generate an appropriate Git branch name from the following instruction content.

Branch naming rules:
1. Use appropriate prefixes like 'feature/', 'bugfix/', 'refactor/', etc.
2. Use only lowercase English letters, numbers, and hyphens (-) (no spaces or special characters)
3. Make it concise and descriptive of the content
4. Use hyphens to separate words
5. Keep it within 50 characters

Instruction content:
{instruction}

Output format:
Output only the branch name. No explanation or surrounding text needed.
            """,
        )

        message = [HumanMessage(content=prompt.format(instruction=instruction))]
        result = self.chat_llm.invoke(message)

        # Remove extra whitespace and newlines for formatting
        branch_name = result.content.strip()

        return branch_name

    def create_working_branch(self, branch_name: str) -> str:
        """Create a working branch.

        Args:
            branch_name (str): Name of the branch to create

        Returns:
            str: Message about creation/switching result
        """
        from src.agent.function.create_branch import CreateBranchFunction

        branch_function = CreateBranchFunction()
        result = branch_function.execute(branch_name=branch_name)

        if result["result"] == "success":
            self.working_branch = branch_name

        return result["message"]

    def run_programmer(self, instruction: str, reviewer_comment: str = None) -> str:
        """Execute the programmer agent.

        Args:
            instruction (str): Instruction to the programmer
            reviewer_comment (str, optional): Comment from reviewer. Defaults to None.

        Returns:
            str: Programmer's output
        """
        return self.programmer_agent.run(instruction, reviewer_comment)

    def run_reviewer(self, programmer_comment: str = None) -> ReviewerOutput:
        """Execute the reviewer agent.

        Args:
            programmer_comment (str, optional): Comment from programmer. Defaults to None.

        Returns:
            ReviewerOutput: Review result
        """
        if not self.working_branch:
            error_msg = (
                "Working branch is not set. Please run create_working_branch() first."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get current local diff (comparison between HEAD and working directory)
        logger.info(f"Getting local diff: working_branch={self.working_branch}")
        diff = self.programmer_agent.get_diff(
            base_branch=self.base_branch,
        )
        logger.info(f"Retrieved diff length: {len(diff)} characters")
        if diff:
            logger.info(f"First 100 characters of diff: {diff[:100]}...")
        else:
            logger.warning("Diff is empty")

        # Execute reviewer agent
        reviewer_input = ReviewerInput(
            diff=diff,
            programmer_comment=programmer_comment,
        )

        return self.reviewer_agent.run(reviewer_input)

    def development_cycle(
        self,
        instruction: str,
        max_iterations: int = 3,
        auto_create_branch: bool = True,
    ) -> dict:
        """Execute the programmer and reviewer cycle.

        Args:
            instruction (str): Initial instruction to the programmer
            max_iterations (int, optional): Maximum number of iterations. Defaults to 3.
            auto_create_branch (bool, optional): Whether to automatically generate and create branch. Defaults to True.

        Returns:
            dict: Execution result of the development cycle

        Raises:
            ValueError: When working branch is not set or there is no diff
        """
        programmer_output = None
        reviewer_output = None

        try:
            # Automatic generation and creation of working branch
            if auto_create_branch and not self.working_branch:
                self.working_branch = self.generate_branch_name(instruction)
                logger.info(f"Generated branch name: {self.working_branch}")

            if not self.working_branch:
                raise ValueError(
                    "Branch name is not set. Please run create_working_branch() first or specify auto_create_branch=True."
                )

            # Execute development cycle
            for i in range(max_iterations):
                logger.info(f"=== Development cycle {i + 1}/{max_iterations} ===")

                programmer_output = self.run_programmer(
                    instruction,
                    reviewer_comment=reviewer_output.summary
                    if reviewer_output
                    else None,
                )
                logger.info(f"Programmer output: {programmer_output[:100]}...")

                reviewer_output = self.run_reviewer(
                    programmer_comment=f"Implementation for development cycle {i + 1} is completed. Please review."
                )
                logger.info(f"Reviewer output: {reviewer_output.summary[:100]}...")

                if reviewer_output.lgtm:
                    logger.info("Review approval (LGTM) obtained. Ending the cycle.")
                    break

            # Check and process diff
            diff = self.programmer_agent.get_diff(
                base_branch=self.base_branch,
            )
            if not diff:
                logger.warning("No local diff found. Cannot create pull request.")
                exit(1)

            try:
                diff_output = subprocess.check_output(
                    [
                        "git",
                        "diff",
                        "--name-only",
                        "HEAD",
                        "--",
                        self.repo_path,
                    ],
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to execute git diff command: {e}")
                raise

            return {
                "programmer_output": programmer_output,
                "reviewer_output": reviewer_output.summary if reviewer_output else None,
                "branch_name": self.working_branch,
            }

        except Exception as e:
            logger.exception(f"Error occurred during development cycle execution: {e}")
            raise
