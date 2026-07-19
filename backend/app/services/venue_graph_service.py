from app.models.domain import RouteStep
from app.repositories.firestore_repo import FirestoreRepository


class VenueGraphService:
    def __init__(self, firestore_repo: FirestoreRepository):
        self.firestore_repo = firestore_repo

    async def route(
        self,
        venue_id: str,
        origin: str,
        destination: str,
        mobility_needs: list[str],
    ) -> list[RouteStep]:
        graph = await self.firestore_repo.get_venue_graph(venue_id)
        if not graph:
            return [self._route_step("Follow venue signage", origin, destination, mobility_needs)]
        return [self._route_step("Use venue graph route", origin, destination, mobility_needs)]

    def _route_step(
        self,
        prefix: str,
        origin: str,
        destination: str,
        mobility_needs: list[str],
    ) -> RouteStep:
        return RouteStep(
            instruction=f"{prefix} from {origin} to {destination}.",
            accessibility_notes=mobility_needs,
        )
