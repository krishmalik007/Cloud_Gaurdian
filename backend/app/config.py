from typing import Optional

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
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", description="Comma-separated list of allowed CORS origins")
    CORS_METHODS: str = Field(default="*", description="Comma-separated list of allowed CORS methods")
    CORS_HEADERS: str = Field(default="*", description="Comma-separated list of allowed CORS headers")
    
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
    OPENSEARCH_VERIFY_CERTS: bool = Field(default=False, description="Verify OpenSearch TLS certificates")
    OPENSEARCH_CA_CERTS: Optional[str] = Field(default=None, description="Path to CA bundle for OpenSearch")
    
    # JWT Config
    JWT_SECRET_KEY: str = Field(..., description="Secret key used to encode/decode JWTs")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm used for JWT signing")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="Number of minutes before an access token expires")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Number of days before a refresh token expires")

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_length(cls, v: str) -> str:
        """
        Enforce a minimum length of 32 characters for the JWT secret key.
        A short or placeholder secret allows attackers to forge JWT tokens.
        Generate a safe key with: python -c "import secrets; print(secrets.token_hex(32))"
        The secret value is intentionally not included in this error message.
        """
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY is too short (minimum 32 characters required). "
                "The application cannot start with a weak JWT secret. "
                "Generate a strong key with: "
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v
    
    # Logging Config
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (e.g., DEBUG, INFO, WARNING, ERROR)")
    LOG_FILE: str = Field(default="app.log", description="File path for rotating file logs")

    # AWS SQS Config (for real-time cloud log ingestion)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS IAM access key ID for SQS access")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS IAM secret access key for SQS access")
    AWS_REGION: str = Field(default="ap-south-1", description="AWS region where the SQS queue is hosted")
    AWS_SQS_QUEUE_URL: Optional[str] = Field(default=None, description="Full URL of the AWS SQS queue to consume from")

    # AWS CloudTrail S3 Ingestion Config (for multi-region batch ingestion)
    CLOUDTRAIL_S3_INGESTION_ENABLED: bool = Field(default=False, description="Enable periodic S3 CloudTrail log ingestion")
    CLOUDTRAIL_S3_BUCKET: Optional[str] = Field(default="aws-cloudtrail-logs-195236889241-96382ad3", description="Central S3 bucket containing CloudTrail logs")
    CLOUDTRAIL_S3_PREFIX: str = Field(default="AWSLogs/195236889241/CloudTrail/", description="S3 prefix for CloudTrail logs")
    CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS: int = Field(default=1, description="Interval in seconds between S3 scans (default 1s)")
    CLOUDTRAIL_S3_REGION: str = Field(default="ap-south-1", description="AWS Region of the S3 bucket")
    CLOUDTRAIL_S3_MAX_FILES_PER_SCAN: int = Field(default=100, description="Maximum number of new log files to process per scan")
    CLOUDTRAIL_S3_BACKFILL_ENABLED: bool = Field(default=False, description="Enable historical log backfill across all past dates")
    CLOUDTRAIL_S3_LOOKBACK_HOURS: int = Field(default=24, description="Lookback window in hours for initial scan when backfill is disabled")
    CLOUDTRAIL_S3_START_DATE: Optional[str] = Field(default=None, description="Optional ISO start date/time (e.g. '2026-10-19T00:00:00Z') for filtering S3 objects")
    CLOUDTRAIL_S3_AWS_PROFILE: Optional[str] = Field(default=None, description="Optional named AWS CLI profile for S3 ingestion (e.g. cloudguardian-s3)")
    CLOUDTRAIL_S3_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="Optional dedicated AWS IAM access key for S3 ingestion")
    CLOUDTRAIL_S3_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="Optional dedicated AWS IAM secret access key for S3 ingestion")
    CLOUDTRAIL_S3_REGIONS: Optional[str] = Field(default=None, description="Optional comma-separated list of AWS regions to discover/ingest (e.g. 'ap-south-1,eu-north-1'). If unset, discovers all regions under prefix.")

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
