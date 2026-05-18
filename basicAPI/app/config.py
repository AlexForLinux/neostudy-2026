from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_url: str
    api_key: str

    advice_prompt: str
    other_prompt: str
    recipe_prompt: str
    search_recipe_prompt: str
    search_advice_prompt: str

    classify_prompt: str

    recipe_docs: str
    advice_docs: str

    sqlite_db: str
    chroma_db: str

    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_base_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()