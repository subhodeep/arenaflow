from typing import Any

from google.cloud import bigquery

from app.core.config import Settings


class BigQueryRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: bigquery.Client | None = None

    @property
    def client(self) -> bigquery.Client:
        if self._client is None:
            self._client = bigquery.Client(project=self.settings.project_id)
        return self._client

    def table(self, table_name: str) -> str:
        return f"{self.settings.project_id}.{self.settings.bigquery_dataset}.{table_name}"

    async def insert_recommendation_event(self, record: dict[str, Any]) -> None:
        errors = self.client.insert_rows_json(self.table("recommendation_events"), [record])
        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")

    async def insert_assistant_event(self, record: dict[str, Any]) -> None:
        errors = self.client.insert_rows_json(self.table("assistant_events"), [record])
        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")

    async def query_recent_crowd_trends(
        self,
        venue_id: str,
        event_id: str | None,
    ) -> list[dict[str, Any]]:
        query = f"""
        SELECT zone_id, AVG(density_score) AS avg_density, MAX(observed_at) AS latest_observed_at
        FROM `{self.table('crowd_observations')}`
        WHERE venue_id = @venue_id
          AND (@event_id IS NULL OR event_id = @event_id)
          AND observed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE)
        GROUP BY zone_id
        ORDER BY avg_density DESC
        LIMIT 20
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("venue_id", "STRING", venue_id),
                bigquery.ScalarQueryParameter("event_id", "STRING", event_id),
            ]
        )
        rows = self.client.query(query, job_config=job_config).result()
        return [dict(row.items()) for row in rows]
