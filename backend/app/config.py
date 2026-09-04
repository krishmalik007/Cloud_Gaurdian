from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
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
    # Ellipsis (...) means this field is REQUIRED. Pydantic will throw an error if it's missing in .env
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., description="Comma-separated list of Kafka broker URLs")
    KAFKA_TOPIC: str = Field(..., description="The main Kafka topic for incoming logs")
    
    # OpenSearch Config
    OPENSEARCH_HOST: str = Field(..., description="Hostname of the OpenSearch cluster")
    OPENSEARCH_PORT: int = Field(default=9200, description="Port of the OpenSearch cluster")
    OPENSEARCH_USERNAME: str = Field(..., description="Admin username for OpenSearch")
    OPENSEARCH_PASSWORD: str = Field(..., description="Admin password for OpenSearch")
    OPENSEARCH_USE_SSL: bool = Field(default=False, description="Whether to use SSL for OpenSearch connection")
    
    # JWT Config
    JWT_SECRET_KEY: str = Field(..., description="Secret key used to encode/decode JWTs")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm used for JWT signing")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="Number of minutes before an access token expires")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Number of days before a refresh token expires")
    
    # Logging Config
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (e.g., DEBUG, INFO, WARNING, ERROR)")
    LOG_FILE: str = Field(default="app.log", description="File path for rotating file logs")

    # AWS SQS Config (for real-time cloud log ingestion)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS IAM access key ID for SQS access")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS IAM secret access key for SQS access")
    AWS_REGION: str = Field(default="ap-south-1", description="AWS region where the SQS queue is hosted")
    AWS_SQS_QUEUE_URL: Optional[str] = Field(default=None, description="Full URL of the AWS SQS queue to consume from")

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
