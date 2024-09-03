"""Get and create secrets in cloud secret manager"""

from typing import Union

from google.cloud import secretmanager


class SecretsManager:
    """Creates and loads secrets from Cloud Secret Manager"""

    def __init__(self) -> None:
        self.secret_client = secretmanager.SecretManagerServiceClient()

    def make_secret(self, project: str | int, secret_name: str, data: str) -> None:
        """Create secret"""
        secret = self.secret_client.create_secret(
            request={
                "parent": f"projects/{project}",
                "secret_id": secret_name,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        _ = self.secret_client.add_secret_version(
            request={"parent": secret.name, "payload": {"data": data.encode("UTF-8")}}
        )

    def get_secret(
        self, project: Union[str, int], secret_name: str, version: Union[str, int] = "latest"
    ) -> str:
        """Get secret from secret manager"""
        name = f"projects/{project}/secrets/{secret_name}/versions/{version}"
        try:
            response = self.secret_client.access_secret_version(request={"name": name})
        except Exception as e:  # pylint: disable=broad-except
            print("Failed to retrieve secret from Secrets Manager:", e)
            return ""

        return response.payload.data.decode("UTF-8")
