from functools import lru_cache

from app.core.config import get_settings
from app.repositories.bigquery_repo import BigQueryRepository
from app.repositories.firestore_repo import FirestoreRepository
from app.repositories.pubsub_repo import PubSubRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.maps_service import MapsService
from app.services.venue_graph_service import VenueGraphService


@lru_cache(maxsize=1)
def get_firestore_repo() -> FirestoreRepository:
    return FirestoreRepository(get_settings())


@lru_cache(maxsize=1)
def get_bigquery_repo() -> BigQueryRepository:
    return BigQueryRepository(get_settings())


@lru_cache(maxsize=1)
def get_pubsub_repo() -> PubSubRepository:
    return PubSubRepository(get_settings())


@lru_cache(maxsize=1)
def get_maps_service() -> MapsService:
    return MapsService(get_settings())


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    return GeminiService(get_settings())


@lru_cache(maxsize=1)
def get_grounding_service() -> GroundingService:
    return GroundingService(get_firestore_repo(), get_bigquery_repo(), get_maps_service())


@lru_cache(maxsize=1)
def get_venue_graph_service() -> VenueGraphService:
    return VenueGraphService(get_firestore_repo())
