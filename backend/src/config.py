import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "mock-key-for-local"
    ANTHROPIC_API_KEY: str = "mock-key-for-local"
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    DATABASE_URL: str = "sqlite:///./plum_claims.db"
    
    # Mock LLM for local evaluation without network costs
    MOCK_EXTRACTION: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
