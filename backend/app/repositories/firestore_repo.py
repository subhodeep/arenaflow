from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from google.cloud import firestore

from app.core.config import Settings


class FirestoreRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: firestore.Client | None = None

    @property
    def client(self) -> firestore.Client:
        if self._client is None:
            self._client = firestore.Client(
                project=self.settings.project_id,
                database=self.settings.firestore_database_id,
            )
        return self._client

    def _collection(self, key: str):
        return self.client.collection(self.settings.collections[key])

    async def get_venue(self, venue_id: str) -> dict[str, Any] | None:
        doc = self._collection("venues").document(venue_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_event(self, event_id: str | None) -> dict[str, Any] | None:
        if not event_id:
            return None
        doc = self._collection("events").document(event_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_crowd_zones(self, venue_id: str) -> list[dict[str, Any]]:
        query = self._collection("crowd_zones").where(filter=firestore.FieldFilter("venue_id", "==", venue_id))
        return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]

    async def get_active_incidents(self, venue_id: str) -> list[dict[str, Any]]:
        query = (
            self._collection("incidents")
            .where(filter=firestore.FieldFilter("venue_id", "==", venue_id))
            .where(filter=firestore.FieldFilter("status", "in", ["open", "investigating", "mitigating"]))
        )
        return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]

    async def get_venue_graph(self, venue_id: str) -> dict[str, Any] | None:
        doc = self._collection("venue_graphs").document(venue_id).get()
        return doc.to_dict() if doc.exists else None

    async def write_assistant_audit(self, record: dict[str, Any]) -> str:
        doc_id = record.get("id") or str(uuid4())
        payload = record | {"created_at": datetime.now(timezone.utc)}
        self._collection("assistant_sessions").document(doc_id).set(payload, merge=True)
        return doc_id

    async def write_ops_snapshot(self, snapshot: dict[str, Any]) -> str:
        doc_id = snapshot.get("id") or str(uuid4())
        payload = snapshot | {"created_at": datetime.now(timezone.utc)}
        self._collection("ops_snapshots").document(doc_id).set(payload, merge=True)
        return doc_id
