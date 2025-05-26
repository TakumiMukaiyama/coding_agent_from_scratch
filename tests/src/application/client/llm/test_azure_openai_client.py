from unittest import TestCase
from unittest.mock import patch

from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.infrastructure.config.agent_setting import agent_settings


class TestAzureOpenAIClient(TestCase):
    def setUp(self):
        self.client = AzureOpenAIClient(
            base_url=agent_settings.AZURE_OPENAI_API_ENDPOINT,
            api_version=agent_settings.AZURE_OPENAI_API_VERSION,
            api_key=agent_settings.AZURE_OPENAI_API_KEY,
            deployment_name=agent_settings.AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O,
            embedding_model=agent_settings.AZURE_OPENAI_EMBEDDING_MODEL,
        )

    def test_initialize_chat(self):
        with patch(
            "src.application.client.llm.azure_openai_client.AzureChatOpenAI"
        ) as mock_chat_openai:
            self.client.initialize_chat()
            mock_chat_openai.assert_called_once()

    def test_initialize_embedding(self):
        with patch(
            "src.application.client.llm.azure_openai_client.AzureOpenAIEmbeddings"
        ) as mock_openai_embeddings:
            self.client.initialize_embedding()
            mock_openai_embeddings.assert_called_once()
