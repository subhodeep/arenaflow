import json
import logging
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.services.gemini.client import GeminiClientProvider
from app.services.gemini.normalizers import GeminiPayloadNormalizer

ResponseT = TypeVar("ResponseT", bound=BaseModel)
logger = logging.getLogger(__name__)


class GeminiJsonGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client_provider = GeminiClientProvider(settings)
        self.normalizer = GeminiPayloadNormalizer()

    @property
    def client(self):
        return self.client_provider.client

    async def generate(
        self,
        prompt: str,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> ResponseT:
        if self.client is None:
            return fallback
        try:
            return self._validated_response(prompt, response_model, fallback)
        except Exception as exc:
            logger.warning(
                "Gemini generation failed; returning fallback. model=%s location=%s "
                "error_type=%s error=%s",
                self.settings.gemini_model,
                self.settings.gemini_location,
                exc.__class__.__name__,
                str(exc)[:500],
            )
            return fallback.model_copy(
                update={
                    "assumptions": [
                        *fallback.assumptions,
                        "Gemini fallback reason: "
                        f"{exc.__class__.__name__}. Check Cloud Run logs for details.",
                    ]
                }
            )

    def normalize_payload(
        self,
        payload,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> dict:
        return self.normalizer.normalize_payload(payload, response_model, fallback)

    def _validated_response(
        self,
        prompt: str,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> ResponseT:
        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config={"response_mime_type": "application/json", "temperature": 0.2},
        )
        payload = json.loads(getattr(response, "text", "") or "{}")
        try:
            return response_model.model_validate(payload)
        except ValidationError:
            normalized = self.normalizer.normalize_payload(payload, response_model, fallback)
            return response_model.model_validate(normalized)
