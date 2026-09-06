from datetime import datetime, timezone

from app.storage.opensearch_client import client
from app.logger import logger


class SessionRepository:
    INDEX_NAME = "cloudguardian_sessions"

    def __init__(self):
        self.client = client
        self._create_index()

    def _create_index(self):
        """
        Create the sessions index if it does not exist.
        """
        try:
            if not self.client.indices.exists(index=self.INDEX_NAME):
                mapping = {
                    "mappings": {
                        "properties": {
                            "session_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "role": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "expires_at": {"type": "date"},
                            "active": {"type": "boolean"}
                        }
                    }
                }
                self.client.indices.create(
                    index=self.INDEX_NAME,
                    body=mapping
                )
                logger.info(f"Created OpenSearch index: {self.INDEX_NAME}")
        except Exception as e:
            logger.error(f"Failed to create index {self.INDEX_NAME}: {e}")

    def create_session(self, session_id: str, user_id: str, role: str, expires_at: str):
        """
        Register a new active session for a user.
        """
        doc = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at,
            "active": True
        }
        try:
            self.client.index(
                index=self.INDEX_NAME,
                id=session_id,
                body=doc,
                refresh=True
            )
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")

    def delete_session(self, session_id: str):
        """
        Remove or deactivate a session on logout.
        """
        try:
            self.client.delete(
                index=self.INDEX_NAME,
                id=session_id,
                refresh=True,
                ignore=[404]
            )
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")

    def count_active_analyst_users(self) -> int:
        """
        Count distinct ANALYST users who currently have an active, unexpired session.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"role": "ANALYST"}},
                        {"term": {"active": True}},
                        {"range": {"expires_at": {"gt": now}}}
                    ]
                }
            },
            "aggs": {
                "distinct_users": {
                    "cardinality": {
                        "field": "user_id"
                    }
                }
            }
        }
        
        try:
            response = self.client.search(
                index=self.INDEX_NAME,
                body=query
            )
            return response["aggregations"]["distinct_users"]["value"]
        except Exception as e:
            logger.error(f"Failed to count active analysts: {e}")
            return 0

    def get_active_user_ids(self) -> set:
        """
        Get a set of all user IDs that currently have an active, unexpired session.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"active": True}},
                        {"range": {"expires_at": {"gt": now}}}
                    ]
                }
            },
            "aggs": {
                "users": {
                    "terms": {
                        "field": "user_id",
                        "size": 10000
                    }
                }
            }
        }
        
        try:
            response = self.client.search(
                index=self.INDEX_NAME,
                body=query
            )
            buckets = response.get("aggregations", {}).get("users", {}).get("buckets", [])
            return {bucket["key"] for bucket in buckets}
        except Exception as e:
            logger.error(f"Failed to get active user ids: {e}")
            return set()


session_repository = SessionRepository()
