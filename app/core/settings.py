from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default=...)

    secret_key: str = Field(default=...)
    algorithm: str = Field(default=...)

    mode: str = Field(default=...)
    debug: bool = False
    show_docs: bool = False
    log_level: str = Field(default=...)

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
