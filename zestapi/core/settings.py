from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="forbid"
    )

    # JWT Configuration
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True  # Default to True for development
    reload: bool = False

    # Rate Limiting
    rate_limit: str = "100/minute"

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Database (example)
    database_url: Optional[str] = None

    # Logging
    log_level: str = "INFO"

    # Plugins
    enabled_plugins: List[str] = []


# Global settings instance
settings = Settings()

# For backward compatibility
JWT_SECRET = settings.jwt_secret
RATE_LIMIT = settings.rate_limit
ENABLED_PLUGINS = settings.enabled_plugins
