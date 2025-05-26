from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool

from src.agent.schema.generate_pr_params_input import GeneratePRParamsInput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.function.base import BaseFunction


class GeneratePullRequestParamsFunction(BaseFunction):
    """Function to generate PR title and description"""

    @staticmethod
    def execute(
        instruction: str,
        programmer_output: str,
        diff: str = "",
    ) -> dict[str, str]:
        """Generate PR title and description

        Args:
            instruction (str): Instructions to the programmer
            programmer_output (str): Output from the programmer
            diff (str, optional): Code diff. Defaults to empty string.

        Returns:
            Dict[str, str]: PR title and description
        """
        try:
            # Initialize LLM client
            llm_client = AzureOpenAIClient()
            chat_llm = llm_client.initialize_chat()

            # Generate PR title
            title_prompt = PromptTemplate.from_template(
                """
You are an expert in creating pull request titles.
Please generate an appropriate pull request title from the following instruction content.

Title rules:
1. Express the changes concisely and clearly
2. Write in English
3. Add appropriate prefix at the beginning (e.g., feat:, fix:, refactor:, docs:, chore:, test:)
4. Keep within 80 characters
5. Write in imperative form (e.g., "Add user authentication")

Instructions to programmer:
{instruction}

Programmer output:
{programmer_output}

Output format:
Output only the title. No explanation or surrounding text is needed.
                """,
            )

            title_message = [
                HumanMessage(
                    content=title_prompt.format(
                        instruction=instruction,
                        programmer_output=programmer_output[:500] if programmer_output else "No output",
                    )
                )
            ]
            title_result = chat_llm.invoke(title_message)
            pr_title = title_result.content.strip()

            # Generate PR description
            description_prompt = PromptTemplate.from_template(
                """
You are an expert in creating pull request descriptions.
Please generate a detailed and understandable pull request description from the following information.

Description rules:
1. Write in markdown format
2. Include the following sections:
   - Overview: Brief description of changes
   - Details: Implementation methods and notable points
   - Testing: How to verify changes (if applicable)
3. Write concisely yet detailed

Instructions to programmer:
{instruction}

Programmer output:
{programmer_output}

Code diff:
{diff}

Output format:
Output the description in markdown format.
                """,
            )

            description_message = [
                HumanMessage(
                    content=description_prompt.format(
                        instruction=instruction,
                        programmer_output=programmer_output[:500] if programmer_output else "No output",
                        diff=diff[:1000] if diff else "No diff",
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
                "message": f"Failed to generate PR parameters: {str(e)}",
                "error": str(e),
            }

    @classmethod
    def to_tool(cls: type["GeneratePullRequestParamsFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Generates pull request title and description.",
            func=cls.execute,
            args_schema=GeneratePRParamsInput,
        )
