from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_url: str
    api_key: str

    advice_prompt: str
    other_prompt: str
    recipe_prompt: str
    search_recipe_prompt: str
    search_advice_prompt: str

    classifier: str
    embeder: str

    recipe_docs: str
    advice_docs: str

    sqlite_db: str
    chroma_db: str

    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()