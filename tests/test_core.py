"""Tests for core Google Forms functionality."""

from unittest.mock import Mock, patch

import pytest

from gforms.core import GFormsClient


class TestGFormsClient:
    """Test cases for GFormsClient."""

    def test_init_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = GFormsClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://forms.googleapis.com/v1"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test client initialization without API key raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Authentication required"):
                GFormsClient()

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "env_test_key"})
    def test_init_with_env_var(self) -> None:
        """Test client initialization with environment variable."""
        client = GFormsClient()
        assert client.api_key == "env_test_key"

    @patch("gforms.core.requests.Session.get")
    def test_get_form_success(self, mock_get: Mock) -> None:
        """Test successful form retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "formId": "test_form",
            "info": {"title": "Test Form"},
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = GFormsClient(api_key="test_key")
        result = client.get_form("test_form")

        assert result["formId"] == "test_form"
        assert result["info"]["title"] == "Test Form"
        mock_get.assert_called_once_with(
            "https://forms.googleapis.com/v1/forms/test_form"
        )

    def test_submit_response_not_implemented(self) -> None:
        """Test that submit_response raises NotImplementedError."""
        client = GFormsClient(api_key="test_key")

        with pytest.raises(NotImplementedError):
            client.submit_response("test_form", {"question1": "answer1"})
