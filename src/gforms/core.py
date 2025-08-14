"""Core Google Forms integration functionality."""

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from .auth import AuthenticationError, GoogleAuthenticator

# Load environment variables
load_dotenv()


class GFormsClient:
    """Client for interacting with Google Forms API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        service_account_path: Optional[str] = None,
        service_account_json: Optional[str] = None,
        use_service_account: bool = False,
    ) -> None:
        """Initialize the Google Forms client.

        Args:
            api_key: Google API key. If not provided, will look for
                GOOGLE_API_KEY env var.
            service_account_path: Path to service account JSON file
            service_account_json: Service account JSON as string
            use_service_account: Whether to use service account authentication

        Raises:
            ValueError: If no valid authentication method is provided
            AuthenticationError: If authentication fails
        """
        self.authenticator = GoogleAuthenticator()
        self._service: Optional[Resource] = None
        self._use_api_key = False

        # Determine authentication method
        if use_service_account or service_account_path or service_account_json:
            # Use service account authentication
            try:
                self.authenticator.authenticate_with_service_account(
                    credentials_path=service_account_path,
                    credentials_json=service_account_json,
                )
                self._service = self.authenticator.get_service()
            except AuthenticationError as e:
                raise AuthenticationError(f"Service account authentication failed: {e}")
        else:
            # Fall back to API key authentication
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "Authentication required. Provide either:\n"
                    "1. API key via api_key parameter or GOOGLE_API_KEY env var, or\n"
                    "2. Service account credentials via service_account_path, "
                    "service_account_json, or environment variables"
                )

            self.base_url = "https://forms.googleapis.com/v1"
            self.session = requests.Session()
            self.session.params = {"key": self.api_key}
            self._use_api_key = True

    @classmethod
    def from_service_account_file(cls, credentials_path: str) -> "GFormsClient":
        """Create client using service account file.

        Args:
            credentials_path: Path to service account JSON file

        Returns:
            Authenticated GFormsClient instance
        """
        return cls(service_account_path=credentials_path, use_service_account=True)

    @classmethod
    def from_service_account_info(
        cls, credentials_info: Dict[str, Any]
    ) -> "GFormsClient":
        """Create client using service account info dictionary.

        Args:
            credentials_info: Service account credentials as dictionary

        Returns:
            Authenticated GFormsClient instance
        """
        import json

        return cls(
            service_account_json=json.dumps(credentials_info), use_service_account=True
        )

    def get_form(self, form_id: str) -> Dict[str, Any]:
        """Retrieve form metadata.

        Args:
            form_id: The Google Form ID.

        Returns:
            Form metadata as dictionary.

        Raises:
            requests.RequestException: If the API request fails (API key auth)
            HttpError: If the API request fails (service account auth)
        """
        if self._use_api_key:
            # Use requests with API key
            url = f"{self.base_url}/forms/{form_id}"
            response = self.session.get(url)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        else:
            # Use Google API client with service account
            if not self._service:
                raise AuthenticationError("Service not initialized")

            try:
                result = self._service.forms().get(formId=form_id).execute()
                return result
            except HttpError as e:
                raise HttpError(f"Failed to get form {form_id}: {e}")

    def list_forms(self) -> Dict[str, Any]:
        """List forms (only available with service account authentication).

        Returns:
            List of forms metadata.

        Raises:
            NotImplementedError: If using API key authentication
            HttpError: If the API request fails
        """
        if self._use_api_key:
            raise NotImplementedError(
                "Listing forms is not supported with API key authentication. "
                "Use service account authentication instead."
            )

        if not self._service:
            raise AuthenticationError("Service not initialized")

        try:
            # Note: This endpoint may not be available in the current Forms API
            # This is a placeholder for when it becomes available
            result = self._service.forms().list().execute()
            return result  # type: ignore[no-any-return]
        except HttpError as e:
            raise HttpError(f"Failed to list forms: {e}")

    def get_form_responses(self, form_id: str) -> Dict[str, Any]:
        """Get form responses (only available with service account authentication).

        Args:
            form_id: The Google Form ID.

        Returns:
            Form responses as dictionary.

        Raises:
            NotImplementedError: If using API key authentication
            HttpError: If the API request fails
        """
        if self._use_api_key:
            raise NotImplementedError(
                "Getting form responses is not supported with API key authentication. "
                "Use service account authentication instead."
            )

        if not self._service:
            raise AuthenticationError("Service not initialized")

        try:
            result = self._service.forms().responses().list(formId=form_id).execute()
            return result  # type: ignore[no-any-return]
        except HttpError as e:
            raise HttpError(f"Failed to get responses for form {form_id}: {e}")

    def submit_response(
        self, form_id: str, responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit a response to a Google Form.

        Args:
            form_id: The Google Form ID.
            responses: Dictionary of question IDs to answers.

        Returns:
            Response metadata as dictionary.

        Raises:
            NotImplementedError: This functionality is not supported by Google Forms API
        """
        # Note: This is a placeholder - actual Google Forms API doesn't
        # support direct submissions. You would typically use the Forms API
        # to get form structure and submit via the public form URL
        raise NotImplementedError(
            "Direct form submission via API is not supported by Google Forms API. "
            "Use the public form URL for submissions."
        )

    @property
    def is_service_account_auth(self) -> bool:
        """Check if using service account authentication."""
        return not self._use_api_key

    @property
    def is_authenticated(self) -> bool:
        """Check if client is properly authenticated."""
        if self._use_api_key:
            return bool(self.api_key)
        else:
            return self.authenticator.is_authenticated
