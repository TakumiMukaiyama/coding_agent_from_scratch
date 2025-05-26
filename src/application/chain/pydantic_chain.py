import logging
import time

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from src.application.chain.base import BaseChain
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.dependency.chaindependency import ChainDependency
from src.application.schema.base import BaseInput

logger = logging.getLogger(__name__)


class PydanticChain(BaseChain):
    """PydanticChain class"""
    prompt: PromptTemplate
    chain: RunnableSequence
    output_schema: type[BaseModel]

    def __init__(
        self,
        chat_llm: AzureChatOpenAI,
        chain_dependency: ChainDependency,
    ):
        self.output_schema = chain_dependency.get_output_schema()
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template=chain_dependency.get_prompt_template(),
            input_variables=chain_dependency.get_input_variables(),
        )
        self.chain = self.prompt | self.chat_llm.with_structured_output(self.output_schema, method="function_calling")

    def get_prompt(self, inputs: BaseInput, **kwargs):
        """Get the prompt string."""
        return self.prompt.invoke(inputs.model_dump(), **kwargs).to_string()

    def invoke_with_retry(self, *args, max_retries: int = 10, llm_client: AzureOpenAIClient, **kwargs):
        """Invoke the chain with retry.
        Args:
            max_retries (int): Maximum number of retries
            llm_client (AzureOpenAIClient | NomuchatClient): LLM client
            *args: Positional arguments to pass to the chain
            **kwargs: Keyword arguments to pass to the chain
        Returns:
            Any: Chain execution result
        Raises:
            Exception: Re-raises exception when error occurs
        """
        try:
            return self.invoke(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            # 429: Rate limit
            if any(msg in error_msg for msg in ["rate limit", "requests", "threshold"]):
                last_error = e
                for attempt in range(max_retries - 1):  # Retry excluding initial execution
                    time.sleep(60)
                    try:
                        return self.invoke(*args, **kwargs)
                    except Exception as retry_e:
                        last_error = retry_e
                        continue
                raise last_error

            # Other errors
            raise e

    def invoke(self, inputs: BaseInput, **kwargs):
        """Invoke the chain."""
        return self.chain.invoke(
            inputs.model_dump(),
            **kwargs,
        )
