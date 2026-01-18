from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_EMBED_MODEL: str = "text-embedding-004"

    STORAGE_DIR: str = "app/storage"
    MAX_UPLOAD_MB: int = 20

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150

    TOP_K: int = 6
    HYBRID_ALPHA: float = 0.5  # 0..1 (0=solo lexical, 1=solo vector)


settings = Settings()
