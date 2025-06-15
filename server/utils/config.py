import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

class Settings():
    AOAI_API_KEY: str = os.getenv("AOAI_API_KEY")
    AOAI_ENDPOINT: str = os.getenv("AOAI_ENDPOINT")
    AOAI_DEPLOY_GPT4O: str = os.getenv("AOAI_DEPLOY_GPT4O")
    AOAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE")
    AOAI_API_VERSION: str = "2024-10-21"

    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Debate Arena API"

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    DB_PATH: str = "history.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///./{DB_PATH}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def get_llm(self):
        """Azure OpenAI LLM 인스턴스를 반환합니다."""
        return AzureChatOpenAI(
            openai_api_key=self.AOAI_API_KEY,
            azure_endpoint=self.AOAI_ENDPOINT,
            azure_deployment=self.AOAI_DEPLOY_GPT4O,
            api_version=self.AOAI_API_VERSION,
            temperature=0.7,
            streaming=True,
        )

    def get_embeddings(self):
        """Azure OpenAI Embeddings 인스턴스를 반환합니다."""
        return AzureOpenAIEmbeddings(
            model=self.AOAI_EMBEDDING_DEPLOYMENT,
            openai_api_version=self.AOAI_API_VERSION,
            api_key=self.AOAI_API_KEY,
            azure_endpoint=self.AOAI_ENDPOINT,
        )


settings = Settings()


def get_llm():
    return settings.get_llm()


def get_embeddings():
    return settings.get_embeddings()