from src.infrastructure.config.agent_setting import agent_settings
from src.infrastructure.utils.logger import get_logger
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings

logger = get_logger(__name__)


class AzureOpenAIClient:
    """Azure OpenAI APIクライアントクラス.

    チャット機能と埋め込み機能を提供する.
    """

    def __init__(
        self,
        base_url: str = None,
        api_version: str = None,
        api_key: str = None,
        deployment_name: str = None,
        embedding_model: str = None,
    ) -> None:
        """コンストラクタ.

        設定ファイルから必要な情報を取得する

        Args:
            base_url: Azure OpenAI APIのエンドポイントURL
            api_version: Azure OpenAI APIのバージョン
            api_key: Azure OpenAI APIのキー
            deployment_name: デプロイメント名
            embedding_model: 埋め込みモデル名
        """
        self.base_url: str = base_url or agent_settings.AZURE_OPENAI_API_ENDPOINT
        self.api_version: str = api_version or agent_settings.AZURE_OPENAI_API_VERSION
        self.api_key: str = api_key or agent_settings.AZURE_OPENAI_API_KEY
        self.deployment_name: str = deployment_name or agent_settings.AZURE_OPENAI_DEPLOYMENT_NAME_GPT_41
        self.embedding_model: str = embedding_model or agent_settings.AZURE_OPENAI_EMBEDDING_MODEL
        self.chat_model: AzureChatOpenAI | None = None
        self.embedding_model_instance: AzureOpenAIEmbeddings | None = None

    def initialize_chat(self) -> AzureChatOpenAI:
        """チャットモデルの初期化.

        Returns:
            ChatOpenAI: 初期化されたチャットモデル
        """
        # o3-miniモデルの場合は parallel_tool_calls を無効化
        if self.deployment_name and "o3-mini" in self.deployment_name:
            return AzureChatOpenAI(
                azure_endpoint=self.base_url,
                azure_deployment=self.deployment_name,
                api_version=self.api_version,
                api_key=self.api_key,
                disabled_params={"parallel_tool_calls": None},
            )
        return AzureChatOpenAI(
            azure_endpoint=self.base_url,
            azure_deployment=self.deployment_name,
            api_version=self.api_version,
            api_key=self.api_key,
        )

    def initialize_embedding(self) -> AzureOpenAIEmbeddings:
        """埋め込みモデルの初期化.

        Returns:
            OpenAIEmbeddings: 初期化された埋め込みモデル
        """
        return AzureOpenAIEmbeddings(
            model=self.embedding_model,
            azure_endpoint=self.base_url,
            azure_deployment=self.embedding_model,
            api_version=self.api_version,
            api_key=self.api_key,
        )
