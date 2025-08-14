"""Configuration management for Google Forms integration."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    # API Key authentication
    google_api_key: Optional[str] = None

    # Service Account authentication
    google_service_account_path: Optional[str] = None
    google_service_account_json: Optional[str] = None
    use_service_account: bool = False

    # OAuth authentication
    google_client_secrets_path: Optional[str] = None
    google_token_path: Optional[str] = None

    # Application settings
    debug: bool = False
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # API Key
        self.google_api_key = self.google_api_key or os.getenv("GOOGLE_API_KEY")

        # Service Account
        self.google_service_account_path = (
            self.google_service_account_path or os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
        )
        self.google_service_account_json = (
            self.google_service_account_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        )
        self.use_service_account = (
            os.getenv("USE_SERVICE_ACCOUNT", "false").lower() == "true"
            or bool(self.google_service_account_path)
            or bool(self.google_service_account_json)
        )

        # OAuth
        self.google_client_secrets_path = self.google_client_secrets_path or os.getenv(
            "GOOGLE_CLIENT_SECRETS_PATH"
        )
        self.google_token_path = self.google_token_path or os.getenv(
            "GOOGLE_TOKEN_PATH", "token.json"
        )

        # Application
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self.google_api_key)

    @property
    def has_service_account(self) -> bool:
        """Check if service account is configured."""
        return bool(
            self.google_service_account_path or self.google_service_account_json
        )

    @property
    def has_oauth_config(self) -> bool:
        """Check if OAuth is configured."""
        return bool(self.google_client_secrets_path)

    def get_auth_method(self) -> str:
        """Get the preferred authentication method."""
        if self.use_service_account and self.has_service_account:
            return "service_account"
        elif self.has_oauth_config:
            return "oauth"
        elif self.has_api_key:
            return "api_key"
        else:
            return "none"


# Global configuration instance
config = Config()
