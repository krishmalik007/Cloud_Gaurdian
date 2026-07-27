from typing import Optional

from app.storage.opensearch_client import client


class UserRepository:
    INDEX_NAME = "users"

    def __init__(self):
        self.client = client
        self._create_index()

    def _create_index(self):
        """
        Create the users index if it does not exist.
        """

        if not self.client.indices.exists(index=self.INDEX_NAME):

            mapping = {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "username": {"type": "keyword"},
                        "email": {"type": "keyword"},
                        "password": {"type": "keyword"},
                        "role": {"type": "keyword"},
                        "enabled": {"type": "boolean"},
                        "created_at": {"type": "date"}
                    }
                }
            }

            self.client.indices.create(
                index=self.INDEX_NAME,
                body=mapping
            )

    # ----------------------------------------------------
    # Create User
    # ----------------------------------------------------
    def create_user(self, user: dict):

        self.client.index(
            index=self.INDEX_NAME,
            id=user["user_id"],
            body=user,
            refresh=True
        )

    # ----------------------------------------------------
    # Get User By Email
    # ----------------------------------------------------
    def get_user_by_email(self, email: str) -> Optional[dict]:

        query = {
            "query": {
                "term": {
                    "email": email
                }
            }
        }

        result = self.client.search(
            index=self.INDEX_NAME,
            body=query
        )

        hits = result["hits"]["hits"]

        if not hits:
            return None

        return hits[0]["_source"]

    # ----------------------------------------------------
    # Get User By ID
    # ----------------------------------------------------
    def get_user_by_id(self, user_id: str) -> Optional[dict]:

        try:
            result = self.client.get(
                index=self.INDEX_NAME,
                id=user_id
            )

            return result["_source"]

        except Exception:
            return None

    # ----------------------------------------------------
    # Get All Users
    # ----------------------------------------------------
    def get_all_users(self):

        result = self.client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            }
        )

        return [
            hit["_source"]
            for hit in result["hits"]["hits"]
        ]

    # ----------------------------------------------------
    # Update User Role
    # ----------------------------------------------------
    def update_role(
        self,
        user_id: str,
        role: str
    ):

        self.client.update(
            index=self.INDEX_NAME,
            id=user_id,
            body={
                "doc": {
                    "role": role
                }
            },
            refresh=True
        )

        return True

    # ----------------------------------------------------
    # Enable / Disable User
    # ----------------------------------------------------
    def update_status(
        self,
        user_id: str,
        enabled: bool
    ):

        self.client.update(
            index=self.INDEX_NAME,
            id=user_id,
            body={
                "doc": {
                    "enabled": enabled
                }
            },
            refresh=True
        )

        return True

    # ----------------------------------------------------
    # Delete User
    # ----------------------------------------------------
    def delete_user(
        self,
        user_id: str
    ):

        try:

            self.client.delete(
                index=self.INDEX_NAME,
                id=user_id,
                refresh=True
            )

            return True

        except Exception:
            return False