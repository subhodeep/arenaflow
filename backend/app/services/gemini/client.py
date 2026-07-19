from typing import Any

from app.core.config import Settings


class GeminiClientProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Any | None = None

    @property
    def client(self) -> Any | None:
        if self.settings.environment == "local" and not self.settings.project_id:
            return None
        if self._client is None:
            from google import genai

            self._client = genai.Client(
                vertexai=self.settings.gemini_use_vertex_ai,
                project=self.settings.project_id,
                location=self.settings.gemini_location,
            )
        return self._client
