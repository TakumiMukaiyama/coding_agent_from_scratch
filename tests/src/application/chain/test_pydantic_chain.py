"""
Unit tests for PydanticChain class

This module implements unit tests for the PydanticChain class.
"""

import unittest
from unittest.mock import MagicMock, patch

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.application.chain.pydantic_chain import PydanticChain
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.dependency.chaindependency import ChainDependency
from src.application.schema.base import BaseInput, BaseOutput


class DummyInput(BaseInput):
    """Input for testing"""

    test_field: str


class DummyOutput(BaseOutput):
    """Output for testing"""

    result: str


class TestPydanticChain(unittest.TestCase):
    """Test cases for PydanticChain class"""

    def setUp(self):
        """Setup before tests"""
        # Create necessary mock objects
        self.mock_chat_llm = MagicMock(spec=ChatOpenAI)

        # Create mock for ChainDependency
        self.mock_chain_dependency = MagicMock(spec=ChainDependency)
        self.mock_chain_dependency.get_output_schema.return_value = DummyOutput
        self.mock_chain_dependency.get_prompt_template.return_value = (
            "Test prompt {test_field}"
        )
        self.mock_chain_dependency.get_input_variables.return_value = ["test_field"]

        # Create PydanticChain instance
        self.chain = PydanticChain(
            chat_llm=self.mock_chat_llm,
            chain_dependency=self.mock_chain_dependency,
        )

        # Test input data
        self.test_input = DummyInput(test_field="Test value")

        # Set up mock chain
        self.mock_chain = MagicMock()
        self.chain.chain = self.mock_chain

    def test_init(self):
        """Test for initialization method"""
        # Check expected values
        self.assertEqual(self.chain.output_schema, DummyOutput)
        self.assertEqual(self.chain.chat_llm, self.mock_chat_llm)

        # Check that the prompt is correctly initialized
        self.assertIsInstance(self.chain.prompt, PromptTemplate)
        self.assertEqual(self.chain.prompt.template, "Test prompt {test_field}")
        self.assertEqual(self.chain.prompt.input_variables, ["test_field"])

    def test_get_prompt(self):
        """Test for get_prompt method"""
        # Set up mock
        mock_prompt_template = MagicMock()
        mock_prompt_invoke_result = MagicMock()
        mock_prompt_template.invoke.return_value = mock_prompt_invoke_result
        mock_prompt_invoke_result.to_string.return_value = "Test prompt Test value"

        self.chain.prompt = mock_prompt_template

        # Execute method
        result = self.chain.get_prompt(self.test_input)

        # Check expected values
        mock_prompt_template.invoke.assert_called_once_with({"test_field": "Test value"})
        mock_prompt_invoke_result.to_string.assert_called_once()
        self.assertEqual(result, "Test prompt Test value")

    def test_invoke(self):
        """Test for invoke method"""
        # Set up mock
        expected_result = {"result": "Test result"}
        self.mock_chain.invoke.return_value = expected_result

        # Execute method
        result = self.chain.invoke(self.test_input)

        # Check expected values
        self.mock_chain.invoke.assert_called_once_with({"test_field": "Test value"})
        self.assertEqual(result, expected_result)

    @patch("time.sleep")
    def test_invoke_with_retry_no_error(self, mock_sleep):
        """Test for invoke_with_retry method when no error occurs"""
        # Set up mock
        expected_result = {"result": "Test result"}
        self.mock_chain.invoke.return_value = expected_result

        # Mock LLM client
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # Execute method
        result = self.chain.invoke_with_retry(
            self.test_input, llm_client=mock_llm_client
        )

        # Check expected values
        self.mock_chain.invoke.assert_called_once_with({"test_field": "Test value"})
        self.assertEqual(result, expected_result)
        # sleep should not be called
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_invoke_with_retry_rate_limit_error(self, mock_sleep):
        """Test for invoke_with_retry method when rate limit error occurs"""
        # First time, raise rate limit error, second time, succeed
        self.mock_chain.invoke.side_effect = [
            Exception("Rate limit exceeded"),
            {"result": "Test result"},
        ]

        # Mock LLM client
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # Execute method
        result = self.chain.invoke_with_retry(
            self.test_input, llm_client=mock_llm_client
        )

        # Check expected values
        self.assertEqual(self.mock_chain.invoke.call_count, 2)
        self.assertEqual(result, {"result": "Test result"})
        # sleep should be called once
        mock_sleep.assert_called_once_with(60)

    @patch("time.sleep")
    def test_invoke_with_retry_max_retries_exceeded(self, mock_sleep):
        """Test for invoke_with_retry method when max retries are exceeded"""
        # Raise rate limit error in all attempts
        rate_limit_error = Exception("Rate limit exceeded")
        self.mock_chain.invoke.side_effect = rate_limit_error

        # Mock LLM client
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # Execute method (should raise an error)
        with self.assertRaises(Exception) as context:
            self.chain.invoke_with_retry(
                self.test_input, max_retries=3, llm_client=mock_llm_client
            )

        # Check expected values
        self.assertEqual(self.mock_chain.invoke.call_count, 3)  # First attempt + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retries, so sleep should be called twice
        self.assertEqual(context.exception, rate_limit_error)

    @patch("time.sleep")
    def test_invoke_with_retry_other_error(self, mock_sleep):
        """Test for invoke_with_retry method when other error occurs"""
        # Raise other error
        other_error = Exception("Other error")
        self.mock_chain.invoke.side_effect = other_error

        # Mock LLM client
        mock_llm_client = MagicMock(spec=AzureOpenAIClient)

        # Execute method (should raise an error)
        with self.assertRaises(Exception) as context:
            self.chain.invoke_with_retry(self.test_input, llm_client=mock_llm_client)

        # Check expected values
        self.mock_chain.invoke.assert_called_once()  # No retry
        mock_sleep.assert_not_called()  # sleep should not be called
        self.assertEqual(context.exception, other_error)


if __name__ == "__main__":
    unittest.main()
