"""Authentication module for Google Forms API."""

import json
import os
from pathlib import Path
from typing import Optional

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class GoogleAuthenticator:
    """Handles authentication for Google APIs."""

    # Google Forms API scope
    SCOPES = ["https://www.googleapis.com/auth/forms.body.readonly"]

    def __init__(self) -> None:
        """Initialize the authenticator."""
        self._credentials: Optional[Credentials] = None
        self._service: Optional[Resource] = None

    def authenticate_with_service_account(
        self,
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None,
    ) -> Credentials:
        """Authenticate using service account credentials.

        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account JSON as string

        Returns:
            Authenticated credentials object

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            if credentials_json:
                # Parse JSON string
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=self.SCOPES
                )
            elif credentials_path:
                # Load from file
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path, scopes=self.SCOPES
                )
            else:
                # Try to get from environment variable
                creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
                creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

                if creds_json:
                    credentials_info = json.loads(creds_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info, scopes=self.SCOPES
                    )
                elif creds_path and Path(creds_path).exists():
                    credentials = service_account.Credentials.from_service_account_file(
                        creds_path, scopes=self.SCOPES
                    )
                else:
                    raise AuthenticationError(
                        "No service account credentials provided. Use "
                        "credentials_path, credentials_json parameter, or set "
                        "GOOGLE_SERVICE_ACCOUNT_PATH/GOOGLE_SERVICE_ACCOUNT_JSON "
                        "environment variable."
                    )

            self._credentials = credentials
            return credentials

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            raise AuthenticationError(
                f"Failed to load service account credentials: {e}"
            )

    def authenticate_with_oauth(
        self, client_secrets_path: str, token_path: Optional[str] = None
    ) -> Credentials:
        """Authenticate using OAuth2 flow.

        Args:
            client_secrets_path: Path to client secrets JSON file
            token_path: Path to store/load token file

        Returns:
            Authenticated credentials object

        Raises:
            AuthenticationError: If authentication fails
        """
        credentials = None
        token_file = token_path or "token.json"

        # Load existing token if available
        if os.path.exists(token_file):
            try:
                credentials = OAuth2Credentials.from_authorized_user_file(
                    token_file, self.SCOPES
                )
            except Exception:
                # Token file is invalid, will need to re-authenticate
                pass

        # If there are no valid credentials, run OAuth flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception:
                    credentials = None

            if not credentials:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_path, self.SCOPES
                    )
                    credentials = flow.run_local_server(port=0)
                except Exception as e:
                    raise AuthenticationError(f"OAuth authentication failed: {e}")

            # Save credentials for next run
            try:
                with open(token_file, "w") as token:
                    token.write(credentials.to_json())
            except Exception:
                # Non-fatal error, just continue
                pass

        self._credentials = credentials
        return credentials

    def get_service(self, service_name: str = "forms", version: str = "v1") -> Resource:
        """Get authenticated Google API service.

        Args:
            service_name: Name of the Google service
            version: API version

        Returns:
            Authenticated service resource

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self._credentials:
            raise AuthenticationError(
                "Not authenticated. Call authenticate_with_service_account() or "
                "authenticate_with_oauth() first."
            )

        if not self._service:
            self._service = build(service_name, version, credentials=self._credentials)

        return self._service

    @property
    def credentials(self) -> Optional[Credentials]:
        """Get current credentials."""
        return self._credentials

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._credentials is not None and self._credentials.valid
