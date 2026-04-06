from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_url: str
    api_key: str

    advice_prompt: str
    other_prompt: str
    recipe_prompt: str

    recipe_docs: str

    sqlite_db: str
    recipe_faiss: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()