"""Unit tests for secret manager"""

from collections import namedtuple
from unittest.mock import MagicMock, patch

import pytest

from secret_manager.secrets import SecretsManager

MockSecret = namedtuple("MockSecret", ["name"])


class MockPayload:  # pylint: disable=too-few-public-methods
    """Mock paylod of a response object"""

    data = b"test-data"


class MockResponse:  # pylint: disable=too-few-public-methods
    """Mock response from secret access"""

    payload = MockPayload()


@pytest.fixture(name="my_secret_manager")
def secret_manager() -> SecretsManager:
    """Pytest fixture for creating SecretManager class object"""
    return SecretsManager()


@patch("google.cloud.secretmanager.SecretManagerServiceClient.add_secret_version")
@patch("google.cloud.secretmanager.SecretManagerServiceClient.create_secret")
def test_make_secret(
    mock_create_secret: MagicMock,
    mock_add_secret_version: MagicMock,
    my_secret_manager: SecretsManager,
) -> None:
    """Test make secret"""
    mock_create_secret.return_value = MockSecret(name="test_name")
    my_secret_manager.make_secret("test_project", "test_secret", "test_data")
    mock_create_secret.assert_called_once_with(
        request={
            "parent": "projects/test_project",
            "secret_id": "test_secret",
            "secret": {"replication": {"automatic": {}}},
        }
    )
    mock_add_secret_version.assert_called_once_with(
        request={"parent": "test_name", "payload": {"data": "test_data".encode("UTF-8")}}
    )


@patch("google.cloud.secretmanager.SecretManagerServiceClient.access_secret_version")
def test_get_secret(
    mock_access: MagicMock,
    my_secret_manager: SecretsManager,
    project: str = "test-proj",
    secret_name: str = "test-secret",
    version: str = "test-ver",
) -> None:
    """Test get secret"""
    mock_access.return_value = MockResponse()
    response = my_secret_manager.get_secret(project, secret_name, version)
    assert response == "test-data"
    name = f"projects/{project}/secrets/{secret_name}/versions/{version}"
    mock_access.assert_called_once_with(request={"name": name})


def test_get_secret_exception(my_secret_manager: SecretsManager) -> None:
    """Test get_secret method handling exceptions."""
    with patch(
        "google.cloud.secretmanager.SecretManagerServiceClient.access_secret_version",
        side_effect=Exception("Mock Error"),
    ):
        response = my_secret_manager.get_secret("test-proj", "test-secret", "test-version")
        assert response == ""
