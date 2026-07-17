from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuration settings for the Cloud Guardian backend.
    Inherits from pydantic-settings BaseSettings which automatically reads from environment variables.
    """

    # Application Config
    APP_NAME: str = Field(default="CloudGuardian", description="Name of the application")
    APP_VERSION: str = Field(default="1.0.0", description="Current version of the application")
    DEBUG: bool = Field(default=False, description="Enable debug mode for development")

    # FastAPI Config
    HOST: str = Field(default="0.0.0.0", description="The host IP address to bind to")
    PORT: int = Field(default=8000, description="The port for the FastAPI server")

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., description="Comma-separated list of Kafka broker URLs")
    KAFKA_TOPIC: str = Field(..., description="The main Kafka topic for incoming logs")

    # OpenSearch Config
    OPENSEARCH_HOST: str = Field(..., description="Hostname of the OpenSearch cluster")
    OPENSEARCH_PORT: int = Field(default=9200, description="Port of the OpenSearch cluster")
    OPENSEARCH_USERNAME: str = Field(..., description="Admin username for OpenSearch")
    OPENSEARCH_PASSWORD: str = Field(..., description="Admin password for OpenSearch")
    OPENSEARCH_USE_SSL: bool = Field(default=False, description="Whether to use SSL for OpenSearch connection")
    OPENSEARCH_VERIFY_CERTS: bool = Field(default=True, description="Whether to verify SSL certificates for OpenSearch")

    # JWT Config
    JWT_SECRET_KEY: str = Field(..., description="Secret key used to encode/decode JWTs")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm used for JWT signing")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="Number of minutes before a JWT expires")

    # Logging Config
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (e.g., DEBUG, INFO, WARNING, ERROR)")
    LOG_FILE: str = Field(default="app.log", description="File path for rotating file logs")

    # CORS Config
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )

    # Rate Limiting
    RATE_LIMIT: str = Field(default="100/minute", description="API rate limit (e.g., '100/minute')")

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Ensure JWT secret key is at least 32 characters for security."""
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Instruct Pydantic to read from the .env file in the same directory (backend/.env)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings object.
    The lru_cache ensures that the .env file is only parsed once and the Settings
    object acts as a Singleton, improving performance.
    """
    return Settings()
