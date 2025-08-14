"""Unittest tests for authentication module."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from gforms.auth import AuthenticationError, GoogleAuthenticator


class TestGoogleAuthenticator(unittest.TestCase):
    """Test GoogleAuthenticator class using unittest framework."""

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        self.authenticator = GoogleAuthenticator()

    def tearDown(self) -> None:
        """Clean up after each test method."""
        # Reset any environment variables that might have been set
        env_vars_to_clean = [
            "GOOGLE_SERVICE_ACCOUNT_PATH",
            "GOOGLE_SERVICE_ACCOUNT_JSON",
        ]
        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]

    def test_init(self) -> None:
        """Test authenticator initialization."""
        self.assertIsNone(self.authenticator._credentials)
        self.assertIsNone(self.authenticator._service)
        self.assertFalse(self.authenticator.is_authenticated)
        self.assertEqual(
            self.authenticator.SCOPES,
            ["https://www.googleapis.com/auth/forms.body.readonly"],
        )

    @patch("gforms.auth.service_account.Credentials.from_service_account_file")
    def test_authenticate_with_service_account_file_success(
        self, mock_from_file: Mock
    ) -> None:
        """Test successful service account authentication with file."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_file.return_value = mock_credentials
        credentials_path = "/path/to/service-account.json"

        # Act
        result = self.authenticator.authenticate_with_service_account(
            credentials_path=credentials_path
        )

        # Assert
        self.assertEqual(result, mock_credentials)
        self.assertEqual(self.authenticator._credentials, mock_credentials)
        mock_from_file.assert_called_once_with(
            credentials_path, scopes=self.authenticator.SCOPES
        )

    @patch("gforms.auth.service_account.Credentials.from_service_account_info")
    def test_authenticate_with_service_account_json_success(
        self, mock_from_info: Mock
    ) -> None:
        """Test successful service account authentication with JSON string."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_info.return_value = mock_credentials
        service_account_json = (
            '{"type": "service_account", "project_id": "test-project"}'
        )
        expected_info = {"type": "service_account", "project_id": "test-project"}

        # Act
        result = self.authenticator.authenticate_with_service_account(
            credentials_json=service_account_json
        )

        # Assert
        self.assertEqual(result, mock_credentials)
        self.assertEqual(self.authenticator._credentials, mock_credentials)
        mock_from_info.assert_called_once_with(
            expected_info, scopes=self.authenticator.SCOPES
        )

    @patch("gforms.auth.service_account.Credentials.from_service_account_file")
    @patch("gforms.auth.Path.exists")
    def test_authenticate_with_env_path_success(
        self, mock_exists: Mock, mock_from_file: Mock
    ) -> None:
        """Test successful service account authentication with environment path."""
        # Arrange
        mock_exists.return_value = True
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_file.return_value = mock_credentials
        env_path = "/env/path/service-account.json"

        with patch.dict(os.environ, {"GOOGLE_SERVICE_ACCOUNT_PATH": env_path}):
            # Act
            result = self.authenticator.authenticate_with_service_account()

            # Assert
            self.assertEqual(result, mock_credentials)
            mock_from_file.assert_called_once_with(
                env_path, scopes=self.authenticator.SCOPES
            )

    @patch("gforms.auth.service_account.Credentials.from_service_account_info")
    def test_authenticate_with_env_json_success(self, mock_from_info: Mock) -> None:
        """Test successful service account authentication with environment JSON."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_info.return_value = mock_credentials
        env_json = '{"type": "service_account", "project_id": "env-project"}'
        expected_info = {"type": "service_account", "project_id": "env-project"}

        with patch.dict(os.environ, {"GOOGLE_SERVICE_ACCOUNT_JSON": env_json}):
            # Act
            result = self.authenticator.authenticate_with_service_account()

            # Assert
            self.assertEqual(result, mock_credentials)
            mock_from_info.assert_called_once_with(
                expected_info, scopes=self.authenticator.SCOPES
            )

    def test_authenticate_with_service_account_no_credentials(self) -> None:
        """Test service account authentication failure when no credentials provided."""
        with self.assertRaises(AuthenticationError) as context:
            self.authenticator.authenticate_with_service_account()

        self.assertIn("No service account credentials provided", str(context.exception))

    @patch("gforms.auth.service_account.Credentials.from_service_account_info")
    def test_authenticate_with_invalid_json(self, mock_from_info: Mock) -> None:
        """Test service account authentication failure with invalid JSON."""
        with self.assertRaises(AuthenticationError) as context:
            self.authenticator.authenticate_with_service_account(
                credentials_json="invalid json string"
            )

        self.assertIn(
            "Failed to load service account credentials", str(context.exception)
        )

    @patch("gforms.auth.service_account.Credentials.from_service_account_file")
    def test_authenticate_with_nonexistent_file(self, mock_from_file: Mock) -> None:
        """Test service account authentication failure with nonexistent file."""
        # Arrange
        mock_from_file.side_effect = FileNotFoundError("File not found")

        # Act & Assert
        with self.assertRaises(AuthenticationError) as context:
            self.authenticator.authenticate_with_service_account(
                credentials_path="/nonexistent/path.json"
            )

        self.assertIn(
            "Failed to load service account credentials", str(context.exception)
        )

    @patch("gforms.auth.build")
    def test_get_service_success(self, mock_build: Mock) -> None:
        """Test successful service creation."""
        # Arrange
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_credentials = Mock()
        mock_credentials.valid = True
        self.authenticator._credentials = mock_credentials

        # Act
        result = self.authenticator.get_service()

        # Assert
        self.assertEqual(result, mock_service)
        self.assertEqual(self.authenticator._service, mock_service)
        mock_build.assert_called_once_with("forms", "v1", credentials=mock_credentials)

    @patch("gforms.auth.build")
    def test_get_service_custom_parameters(self, mock_build: Mock) -> None:
        """Test service creation with custom service name and version."""
        # Arrange
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_credentials = Mock()
        mock_credentials.valid = True
        self.authenticator._credentials = mock_credentials

        # Act
        result = self.authenticator.get_service(service_name="sheets", version="v4")

        # Assert
        self.assertEqual(result, mock_service)
        mock_build.assert_called_once_with("sheets", "v4", credentials=mock_credentials)

    def test_get_service_not_authenticated(self) -> None:
        """Test service creation failure when not authenticated."""
        with self.assertRaises(AuthenticationError) as context:
            self.authenticator.get_service()

        self.assertIn("Not authenticated", str(context.exception))

    @patch("gforms.auth.build")
    def test_get_service_cached(self, mock_build: Mock) -> None:
        """Test that service is cached after first creation."""
        # Arrange
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_credentials = Mock()
        mock_credentials.valid = True
        self.authenticator._credentials = mock_credentials

        # Act
        result1 = self.authenticator.get_service()
        result2 = self.authenticator.get_service()

        # Assert
        self.assertEqual(result1, result2)
        self.assertEqual(result1, mock_service)
        # build should only be called once due to caching
        mock_build.assert_called_once()

    def test_credentials_property_none(self) -> None:
        """Test credentials property when no credentials set."""
        self.assertIsNone(self.authenticator.credentials)

    def test_credentials_property_set(self) -> None:
        """Test credentials property when credentials are set."""
        mock_credentials = Mock()
        self.authenticator._credentials = mock_credentials
        self.assertEqual(self.authenticator.credentials, mock_credentials)

    def test_is_authenticated_false_no_credentials(self) -> None:
        """Test is_authenticated property when no credentials."""
        self.assertFalse(self.authenticator.is_authenticated)

    def test_is_authenticated_false_invalid_credentials(self) -> None:
        """Test is_authenticated property when credentials are invalid."""
        mock_credentials = Mock()
        mock_credentials.valid = False
        self.authenticator._credentials = mock_credentials
        self.assertFalse(self.authenticator.is_authenticated)

    def test_is_authenticated_true_valid_credentials(self) -> None:
        """Test is_authenticated property when credentials are valid."""
        mock_credentials = Mock()
        mock_credentials.valid = True
        self.authenticator._credentials = mock_credentials
        self.assertTrue(self.authenticator.is_authenticated)

    @patch("gforms.auth.InstalledAppFlow.from_client_secrets_file")
    @patch("gforms.auth.OAuth2Credentials.from_authorized_user_file")
    @patch("os.path.exists")
    def test_authenticate_with_oauth_new_flow(
        self, mock_exists: Mock, mock_from_file: Mock, mock_flow_class: Mock
    ) -> None:
        """Test OAuth authentication with new flow."""
        # Arrange
        mock_exists.return_value = False  # No existing token
        mock_flow = Mock()
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_flow.run_local_server.return_value = mock_credentials
        mock_flow_class.return_value = mock_flow

        client_secrets_path = "/path/to/client_secrets.json"

        # Act
        result = self.authenticator.authenticate_with_oauth(client_secrets_path)

        # Assert
        self.assertEqual(result, mock_credentials)
        self.assertEqual(self.authenticator._credentials, mock_credentials)
        mock_flow_class.assert_called_once_with(
            client_secrets_path, self.authenticator.SCOPES
        )
        mock_flow.run_local_server.assert_called_once_with(port=0)

    @patch("gforms.auth.OAuth2Credentials.from_authorized_user_file")
    @patch("os.path.exists")
    def test_authenticate_with_oauth_existing_valid_token(
        self, mock_exists: Mock, mock_from_file: Mock
    ) -> None:
        """Test OAuth authentication with existing valid token."""
        # Arrange
        mock_exists.return_value = True
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_file.return_value = mock_credentials

        client_secrets_path = "/path/to/client_secrets.json"

        # Act
        result = self.authenticator.authenticate_with_oauth(client_secrets_path)

        # Assert
        self.assertEqual(result, mock_credentials)
        self.assertEqual(self.authenticator._credentials, mock_credentials)
        mock_from_file.assert_called_once_with("token.json", self.authenticator.SCOPES)

    @patch("gforms.auth.InstalledAppFlow.from_client_secrets_file")
    def test_authenticate_with_oauth_flow_failure(self, mock_flow_class: Mock) -> None:
        """Test OAuth authentication failure during flow."""
        # Arrange
        mock_flow_class.side_effect = Exception("OAuth flow failed")
        client_secrets_path = "/path/to/client_secrets.json"

        # Act & Assert
        with self.assertRaises(AuthenticationError) as context:
            self.authenticator.authenticate_with_oauth(client_secrets_path)

        self.assertIn("OAuth authentication failed", str(context.exception))


class TestGoogleAuthenticatorIntegration(unittest.TestCase):
    """Integration tests for GoogleAuthenticator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.authenticator = GoogleAuthenticator()

    def test_full_service_account_workflow(self) -> None:
        """Test complete service account authentication workflow."""
        # Create a temporary service account file
        service_account_data = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "key-id",
            "private_key": (
                "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
            ),
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(service_account_data, f)
            temp_file_path = f.name

        try:
            # This would normally work with real credentials
            # For testing, we expect it to fail with authentication error
            with self.assertRaises(Exception):
                self.authenticator.authenticate_with_service_account(
                    credentials_path=temp_file_path
                )
        finally:
            # Clean up
            os.unlink(temp_file_path)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
