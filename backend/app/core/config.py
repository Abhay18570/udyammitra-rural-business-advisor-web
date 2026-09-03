from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    app_name: str = "UdyamMitra API"
    app_env: Literal["development", "testing", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://"
    frontend_url: AnyHttpUrl = "http://localhost:5173"
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() in {"release", "production"}:
            return False
        return value

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if self.app_env in {"staging", "production"} and (not self.jwt_secret_key or len(self.jwt_secret_key) < 32):
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters outside development/testing.")
        return self

    @property
    def docs_enabled(self) -> bool:
        return self.app_env != "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
