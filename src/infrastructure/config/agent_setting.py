import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Settings for agent"""

    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = ""
    AZURE_OPENAI_API_ENDPOINT: str = ""
    AZURE_OPENAI_EMBEDDING_MODEL: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O_MINI: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME_O3_MINI: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME_GPT_41: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env"),
        case_sensitive=True,
        extra="ignore",
    )


agent_settings = AgentSettings()
