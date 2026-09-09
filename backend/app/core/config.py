from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
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

    nearby_market_provider: Literal["overpass", "google"] = "overpass"
    google_places_api_key: Optional[SecretStr] = Field(default=None, repr=False)
    google_places_base_url: AnyHttpUrl = "https://places.googleapis.com/v1/places:searchNearby"
    google_places_text_search_url: AnyHttpUrl = "https://places.googleapis.com/v1/places:searchText"
    google_places_text_max_pages: int = Field(default=2, ge=1, le=3)

    @field_validator("google_places_text_search_url")
    @classmethod
    def google_text_endpoint(cls, value):
        if str(value) != "https://places.googleapis.com/v1/places:searchText":
            raise ValueError("Google Text Search requires the official HTTPS endpoint")
        return value

    google_places_timeout_seconds: float = Field(default=15, gt=0, le=25)
    google_places_max_results: int = Field(default=20, ge=1, le=20)

    @field_validator("google_places_base_url")
    @classmethod
    def google_endpoint(cls, value):
        # Never send the API key to a redirect, query string or arbitrary host.
        if str(value) != "https://places.googleapis.com/v1/places:searchNearby":
            raise ValueError("Google Places endpoint must be the official HTTPS Nearby Search endpoint")
        return value

    nominatim_base_url: AnyHttpUrl = "https://nominatim.openstreetmap.org"
    osm_user_agent: str = Field(default="UdyamMitra-SIH/0.1 (locality and business evidence)", min_length=15, max_length=250)
    geocoding_timeout_seconds: float = Field(default=8, gt=0, le=15)
    geocoding_min_interval_seconds: float = Field(default=1.1, ge=1, le=60)
    geocoding_cache_ttl_seconds: int = Field(default=2592000, ge=60)
    geocoding_negative_cache_ttl_seconds: int = Field(default=3600, ge=60)
    overpass_base_url: AnyHttpUrl = "https://overpass-api.de/api/interpreter"
    overpass_timeout_seconds: float = Field(default=25, gt=0, le=40)
    overpass_query_timeout_seconds: int = Field(default=20, ge=1, le=35)
    overpass_max_response_bytes: int = Field(default=5000000, ge=1024, le=20000000)
    overpass_max_elements: int = Field(default=5000, ge=1, le=10000)
    overpass_max_concurrent_requests: int = Field(default=1, ge=1, le=2)
    nearby_request_timeout_seconds: float = Field(default=50, ge=10, le=55)
    nearby_cache_ttl_seconds: int = Field(default=86400, ge=60)
    nearby_empty_cache_ttl_seconds: int = Field(default=3600, ge=60)
    nearby_stale_max_age_seconds: int = Field(default=604800, ge=0, le=2592000)

    @field_validator("osm_user_agent")
    @classmethod
    def valid_osm_agent(cls, value):
        if any(char in value for char in ("\r", "\n")) or not value.isascii():
            raise ValueError("OSM User-Agent must be a single ASCII application identifier.")
        return value

    @model_validator(mode="after")
    def provider_budget(self):
        if self.overpass_query_timeout_seconds >= self.overpass_timeout_seconds:
            raise ValueError("Overpass HTTP timeout must exceed its query timeout.")
        if 2 * self.geocoding_timeout_seconds + self.overpass_timeout_seconds + 3 > self.nearby_request_timeout_seconds:
            raise ValueError("Nearby request budget must cover geocoding fallback and Overpass.")
        return self

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
