from typing import Any

import httpx

from app.core.config import Settings
from app.models.requests import BaseArenaRequest, NavigationRouteRequest, TransportationOptionsRequest


class MapsService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def context_for_request(self, request: BaseArenaRequest) -> dict[str, Any]:
        if not self.settings.maps_server_api_key:
            return {"available": False, "reason": "MAPS_SERVER_API_KEY is not configured"}
        if isinstance(request, NavigationRouteRequest):
            return await self.route_context(request.origin, request.destination)
        if isinstance(request, TransportationOptionsRequest):
            return await self.place_context(request.origin_address)
        return {"available": False, "reason": "No maps adapter for request type"}

    async def route_context(self, origin: str, destination: str) -> dict[str, Any]:
        return {"available": True, "origin": origin, "destination": destination, "note": "Server-side Maps route adapter placeholder. Configure Routes API request as needed."}

    async def place_context(self, address: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            _ = client
        return {"available": True, "address": address, "note": "Server-side Places adapter placeholder. Configure Places API request as needed."}
