from app.models.domain import RouteStep
from app.repositories.firestore_repo import FirestoreRepository


class VenueGraphService:
    def __init__(self, firestore_repo: FirestoreRepository):
        self.firestore_repo = firestore_repo

    async def route(self, venue_id: str, origin: str, destination: str, mobility_needs: list[str]) -> list[RouteStep]:
        graph = await self.firestore_repo.get_venue_graph(venue_id)
        if not graph:
            return [RouteStep(instruction=f"Follow venue signage from {origin} to {destination}.", accessibility_notes=mobility_needs)]
        return [RouteStep(instruction=f"Use venue graph route from {origin} to {destination}.", accessibility_notes=mobility_needs)]
