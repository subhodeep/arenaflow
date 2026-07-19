import json
from typing import Any

from google.cloud import pubsub_v1

from app.core.config import Settings


class PubSubRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._publisher: pubsub_v1.PublisherClient | None = None

    @property
    def publisher(self) -> pubsub_v1.PublisherClient:
        if self._publisher is None:
            self._publisher = pubsub_v1.PublisherClient()
        return self._publisher

    def topic_path(self, topic_name: str) -> str:
        return self.publisher.topic_path(self.settings.project_id, topic_name)

    async def _publish(self, topic_name: str, event: dict[str, Any]) -> str:
        data = json.dumps(event, default=str).encode("utf-8")
        future = self.publisher.publish(self.topic_path(topic_name), data)
        return future.result(timeout=10)

    async def publish_operations_event(self, event: dict[str, Any]) -> str:
        return await self._publish(self.settings.pubsub_topic_operations, event)

    async def publish_crowd_signal(self, event: dict[str, Any]) -> str:
        return await self._publish(self.settings.pubsub_topic_crowd, event)

    async def publish_sustainability_event(self, event: dict[str, Any]) -> str:
        return await self._publish(self.settings.pubsub_topic_sustainability, event)
