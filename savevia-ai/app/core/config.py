from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT", default=3306)
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=5, alias="DB_MAX_OVERFLOW")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Redis
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT", default=6379)
    redis_db: int = Field(default=0, alias="REDIS_DB")

    # JWT
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # Java service URLs
    user_service_url: str = Field(alias="USER_SERVICE_URL")
    card_service_url: str = Field(alias="CARD_SERVICE_URL")
    http_timeout_seconds: float = Field(default=10.0, alias="HTTP_TIMEOUT_SECONDS")
    http_connect_timeout_seconds: float = Field(default=2.0, alias="HTTP_CONNECT_TIMEOUT_SECONDS")

    # OpenAI / LangGraph (used in later phases — declared now for completeness)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com", alias="OPENAI_BASE_URL")

    # Service identity
    service_name: str = Field(default="savevia-ai", alias="SERVICE_NAME")
    service_port: int = Field(default=8002, alias="SERVICE_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Public-facing URLs used by saved-result share-link generation + OG page
    frontend_url: str = Field(default="https://savevia.app", alias="FRONTEND_URL")
    share_base_url: str = Field(default="http://localhost:5173", alias="SHARE_BASE_URL")

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @property
    def db_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


def reset_settings_cache() -> None:
    """Reset the cached Settings — call in tests after modifying env vars."""
    get_settings.cache_clear()
