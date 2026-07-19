r"""Seed ArenaFlow demo data into Firestore.

Usage from the repository root:

    $env:PROJECT_ID="your-gcp-project-id"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install google-cloud-firestore
    python scripts\seed_demo_data.py

Optional environment variables:

    FIRESTORE_DATABASE_ID=(default)
    DEMO_VENUE_ID=demo-venue
    DEMO_EVENT_ID=demo-match

The script is idempotent: running it again overwrites the same demo documents.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud import firestore

PROJECT_ID = os.environ.get("PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
FIRESTORE_DATABASE_ID = os.environ.get("FIRESTORE_DATABASE_ID", "(default)")
DEMO_VENUE_ID = os.environ.get("DEMO_VENUE_ID", "demo-venue")
DEMO_EVENT_ID = os.environ.get("DEMO_EVENT_ID", "demo-match")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def set_doc(client: firestore.Client, collection: str, doc_id: str, data: dict[str, Any]) -> None:
    payload = data | {"updated_at": utc_now(), "seeded_by": "arenaflow-demo-seed"}
    client.collection(collection).document(doc_id).set(payload)
    print(f"seeded {collection}/{doc_id}")


def main() -> None:
    if not PROJECT_ID:
        raise SystemExit("PROJECT_ID or GOOGLE_CLOUD_PROJECT environment variable is required")

    client = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE_ID)
    kickoff = utc_now() + timedelta(hours=5)

    set_doc(
        client,
        "venues",
        DEMO_VENUE_ID,
        {
            "name": "ArenaFlow Demo Stadium",
            "city": "Toronto",
            "country": "Canada",
            "timezone": "America/Toronto",
            "capacity": 68000,
            "gates": [
                {"id": "gate-a", "name": "Gate A", "type": "accessible", "status": "open", "queue_minutes": 6},
                {"id": "gate-b", "name": "Gate B", "type": "general", "status": "open", "queue_minutes": 14},
                {"id": "gate-c", "name": "Gate C", "type": "general", "status": "congested", "queue_minutes": 24},
                {"id": "gate-d", "name": "Gate D", "type": "staff_emergency", "status": "restricted", "queue_minutes": 0},
            ],
            "sections": [
                {"id": "section-118", "name": "Section 118", "level": "lower", "nearest_gate": "Gate A"},
                {"id": "section-120", "name": "Section 120", "level": "lower", "nearest_gate": "Gate A"},
                {"id": "section-205", "name": "Section 205", "level": "club", "nearest_gate": "Gate B"},
                {"id": "section-310", "name": "Section 310", "level": "upper", "nearest_gate": "Gate C"},
            ],
            "amenities": [
                {"type": "water_refill", "name": "Refill Station North", "location": "North Concourse near Section 118"},
                {"type": "water_refill", "name": "Refill Station East", "location": "East Concourse near Section 205"},
                {"type": "first_aid", "name": "First Aid North", "location": "Behind Section 120"},
                {"type": "restroom", "name": "Accessible Restrooms", "location": "Sections 118, 120, 205"},
                {"type": "info", "name": "Accessibility Services Desk", "location": "Inside Gate A"},
                {"type": "sensory", "name": "Low-Sensory Room", "location": "West Concourse, Level 1"},
            ],
            "accessibility_features": [
                "step-free route from Gate A to Sections 118 and 120",
                "elevators at North Concourse and West Concourse",
                "wheelchair seating near Section 120",
                "low-sensory room on West Concourse",
                "service animal relief area outside Gate A",
                "hearing loop available at guest services desks",
            ],
            "transportation": {
                "transit_hub": "Union Station shuttle platform",
                "accessible_pickup": "North Plaza accessible pickup zone",
                "rideshare": "East Lot rideshare area",
                "bike_parking": "South Greenway bike valet",
                "post_match_egress": "Use North Plaza for transit shuttles; avoid East Lot for 20 minutes after final whistle",
            },
            "sustainability": {
                "waste_streams": ["recycling", "compost", "landfill"],
                "refill_policy": "Reusable bottles are encouraged. Refill stations are available after security screening.",
                "low_carbon_tip": "Transit shuttles from Union Station are the lowest-carbon recommended arrival path.",
            },
        },
    )

    set_doc(
        client,
        "events",
        DEMO_EVENT_ID,
        {
            "venue_id": DEMO_VENUE_ID,
            "name": "FIFA World Cup 2026 Demo Match",
            "home_team": "Canada",
            "away_team": "Japan",
            "kickoff_time": kickoff,
            "expected_attendance": 64000,
            "phase": "pre_match_ingress",
            "weather_summary": "Warm evening, light wind, no rain expected",
            "staffing_notes": [
                "Accessibility volunteers staged at Gate A and North Concourse",
                "Crowd flow team monitoring Gate C and East Concourse",
                "Transit volunteers assigned to North Plaza shuttle queues",
            ],
        },
    )

    crowd_zones = {
        "demo-zone-gate-a": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "zone_id": "gate-a",
            "name": "Gate A Accessible Entry",
            "density_score": 0.34,
            "status": "normal",
            "queue_minutes": 6,
            "recommendation": "Recommended accessible entry point",
            "observed_at": utc_now(),
        },
        "demo-zone-gate-c": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "zone_id": "gate-c",
            "name": "Gate C East Entry",
            "density_score": 0.86,
            "status": "high_pressure",
            "queue_minutes": 24,
            "recommendation": "Divert late arrivals toward Gate B and Gate A overflow lanes",
            "observed_at": utc_now(),
        },
        "demo-zone-north-concourse": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "zone_id": "north-concourse",
            "name": "North Concourse",
            "density_score": 0.48,
            "status": "moderate",
            "queue_minutes": 8,
            "recommendation": "Keep step-free path clear for wheelchair users and families",
            "observed_at": utc_now(),
        },
        "demo-zone-east-lot": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "zone_id": "east-lot",
            "name": "East Rideshare Lot",
            "density_score": 0.72,
            "status": "building",
            "queue_minutes": 18,
            "recommendation": "Delay rideshare messaging until 20 minutes after match end",
            "observed_at": utc_now(),
        },
    }
    for doc_id, data in crowd_zones.items():
        set_doc(client, "crowd_zones", doc_id, data)

    incidents = {
        "demo-incident-elevator-west": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "title": "West Concourse elevator intermittent delay",
            "status": "investigating",
            "severity": "medium",
            "location": "West Concourse elevator bank",
            "summary": "One elevator is intermittently slow. North Concourse elevators remain operational.",
            "owner": "Accessibility Operations Lead",
            "created_at": utc_now() - timedelta(minutes=18),
            "recommended_action": "Route wheelchair users from Gate A through North Concourse elevators until West elevator status is confirmed.",
        },
        "demo-incident-gate-c-pressure": {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "title": "Gate C queue pressure rising",
            "status": "mitigating",
            "severity": "high",
            "location": "Gate C exterior plaza",
            "summary": "Gate C queue length is increasing due to late arrivals and bag checks.",
            "owner": "Crowd Flow Supervisor",
            "created_at": utc_now() - timedelta(minutes=11),
            "recommended_action": "Send multilingual volunteers to redirect non-accessibility guests toward Gate B overflow lanes.",
        },
    }
    for doc_id, data in incidents.items():
        set_doc(client, "incidents", doc_id, data)

    set_doc(
        client,
        "venue_graphs",
        DEMO_VENUE_ID,
        {
            "venue_id": DEMO_VENUE_ID,
            "nodes": [
                {"id": "gate-a", "label": "Gate A", "type": "gate", "accessible": True},
                {"id": "north-concourse", "label": "North Concourse", "type": "concourse", "accessible": True},
                {"id": "section-118", "label": "Section 118", "type": "section", "accessible": True},
                {"id": "section-120", "label": "Section 120", "type": "section", "accessible": True},
                {"id": "first-aid-north", "label": "First Aid North", "type": "amenity", "accessible": True},
                {"id": "refill-north", "label": "Refill Station North", "type": "amenity", "accessible": True},
            ],
            "edges": [
                {"from": "gate-a", "to": "north-concourse", "minutes": 4, "step_free": True, "crowd_level": "normal"},
                {"from": "north-concourse", "to": "section-120", "minutes": 5, "step_free": True, "crowd_level": "moderate"},
                {"from": "north-concourse", "to": "section-118", "minutes": 4, "step_free": True, "crowd_level": "moderate"},
                {"from": "north-concourse", "to": "first-aid-north", "minutes": 2, "step_free": True, "crowd_level": "normal"},
                {"from": "north-concourse", "to": "refill-north", "minutes": 2, "step_free": True, "crowd_level": "normal"},
            ],
            "recommended_accessible_route": ["gate-a", "north-concourse", "section-120"],
            "avoid_zones": ["gate-c", "east-lot"],
        },
    )

    set_doc(
        client,
        "sustainability_metrics",
        "demo-sustainability-current",
        {
            "venue_id": DEMO_VENUE_ID,
            "event_id": DEMO_EVENT_ID,
            "water_refill_station_status": "normal",
            "recycling_bin_capacity": "62%",
            "compost_bin_capacity": "48%",
            "landfill_bin_capacity": "57%",
            "transit_mode_share_estimate": "54%",
            "recommended_nudge": "Promote North Concourse refill stations and Union Station shuttle route.",
            "observed_at": utc_now(),
        },
    )

    print("\nDemo data seeded successfully.")
    print(f"Use Venue ID: {DEMO_VENUE_ID}")
    print(f"Use Event ID: {DEMO_EVENT_ID}")


if __name__ == "__main__":
    main()
