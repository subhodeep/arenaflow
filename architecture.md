# ArenaFlow Architecture

ArenaFlow is a GenAI-enabled stadium operations and tournament experience platform for FIFA World Cup 2026 venues. It supports fans, volunteers, organizers, venue staff, accessibility teams, transport coordinators, and sustainability teams with multilingual assistance and real-time operational intelligence.

## 1. Architecture goals

- Use Google Gemini 2.5 Pro on Vertex AI through Application Default Credentials (ADC) from the backend Cloud Run service account. Do not use Gemini API keys.
- Keep all environment-specific values in environment variables or secrets. Do not hard-code project IDs, API keys, service URLs, CORS origins, model names, collection names, topic names, or dataset names in application code.
- Deploy from a local machine with Google Cloud CLI without local Docker builds. Container images are built remotely by Cloud Build using Dockerfiles with pinned runtimes.
- Use least-privilege service accounts for runtime components.
- Separate public fan experiences from staff/operations workflows at the application authorization layer.
- Support accessibility, multilingual UX, sustainability guidance, transportation planning, navigation, crowd management, and real-time decision support.

## 2. High-level component diagram

```text
+-----------------------------+        HTTPS         +-----------------------------+
| React PWA on Cloud Run      | -------------------> | Python FastAPI on Cloud Run |
| - Fan navigation            |                      | - API gateway               |
| - Multilingual assistant    |                      | - Gemini orchestration      |
| - Accessibility views       |                      | - Operational intelligence  |
| - Staff console             |                      | - Staff decision support    |
+--------------+--------------+                      +------+-----------+----------+
               |                                            |           |
               | Runtime /config.js                         |           |
               v                                            v           v
+-----------------------------+                 +----------------+  +----------------+
| Google Maps Platform        |                 | Secret Manager |  | Firestore      |
| - Maps JavaScript API       |                 | - Gemini key   |  | - Live state   |
| - Routes API                |                 | - Maps key     |  | - Incidents    |
| - Places API                |                 +----------------+  | - Venue graph  |
+-----------------------------+                                      +----------------+
                                                                    |           |
                                                                    v           v
                                                          +----------------+  +----------------+
                                                          | Pub/Sub        |  | BigQuery       |
                                                          | - Ops events   |  | - Analytics    |
                                                          | - Crowd signals|  | - Trends       |
                                                          +----------------+  +----------------+
                                                                    |
                                                                    v
                                                          +----------------+
                                                          | Cloud Scheduler|
                                                          | - Ops snapshots|
                                                          +----------------+
```

## 3. Google Cloud services

| Service | Purpose |
| --- | --- |
| Cloud Run | Hosts the React frontend server and Python FastAPI backend as independently deployable services. |
| Cloud Build | Builds backend and frontend container images remotely from Dockerfiles. No local Docker build is required. |
| Artifact Registry | Stores Cloud Build-generated container images. |
| Secret Manager | Stores only optional non-Gemini secrets such as a restricted Maps browser key when organizational policy allows it. Gemini API keys are not used. |
| Vertex AI API | Provides Gemini 2.5 Pro access using Cloud Run service account ADC and IAM. |
| Firestore Native Mode | Stores live operational state, venue graph data, incidents, crowd zones, route annotations, accessibility notes, and assistant sessions. |
| Pub/Sub | Carries operations events, crowd signals, sustainability events, and asynchronous decision-support work. |
| BigQuery | Stores aggregated events, decision-support outputs, sustainability metrics, and post-event analytics. |
| Cloud Scheduler | Invokes periodic operational snapshot and recommendation refresh jobs. |
| Cloud Logging, Monitoring, Trace, Error Reporting | Observability for security, reliability, latency, Gemini failures, and operational events. |
| Google Maps Platform APIs | Improves navigation, routes, transport options, and place-aware fan guidance. |

## 4. Application surfaces

### 4.1 Fan experience

- Multilingual chat assistant for match-day questions.
- Accessible route suggestions with elevator, ramp, low-sensory, restroom, first-aid, wheelchair, and step-free filters.
- Stadium wayfinding using venue graph data and Google Maps context.
- Transportation guidance for public transit, rideshare, shuttles, accessible pickup, walking routes, and post-match egress.
- Sustainability nudges such as refill station suggestions, waste sorting guidance, low-carbon route options, and congestion-aware recommendations.

### 4.2 Staff and organizer experience

- Crowd heatmap and zone recommendations.
- Incident summarization and multilingual volunteer guidance.
- Real-time decision-support panel powered by Gemini 2.5 Pro using grounded operational context.
- Staffing and volunteer task suggestions.
- Sustainability and transport operations summaries.
- Exportable operational timeline and post-event analytics.

## 5. Backend architecture

The backend is a Python FastAPI service with the following modules:

```text
backend/
  app/
    main.py
    core/
      config.py              # Pydantic settings from env/secrets only
      security.py            # Auth, CORS, headers, request validation
      logging.py             # Structured logging and correlation IDs
    api/
      routes/
        health.py
        assistant.py
        navigation.py
        crowd.py
        accessibility.py
        transportation.py
        sustainability.py
        operations.py
    services/
      gemini_service.py      # Gemini 2.5 Pro client and JSON schema handling
      grounding_service.py   # Retrieves Firestore/BigQuery/Maps context
      venue_graph_service.py # Internal stadium graph routing
      maps_service.py        # Routes/Places adapters
      crowd_service.py
      ops_intel_service.py
      sustainability_service.py
    repositories/
      firestore_repo.py
      bigquery_repo.py
      pubsub_repo.py
    models/
      requests.py
      responses.py
      domain.py
    tests/
```

### 5.1 Gemini orchestration

Gemini 2.5 Pro is used through Vertex AI with Application Default Credentials from the backend Cloud Run service account. No Gemini API key is stored, mounted, returned, or logged.

Gemini calls must be grounded with structured context assembled by the backend:

- Current venue, event, kickoff time, gate status, crowd zones, incidents, routes, weather/transport notes if available, accessibility constraints, sustainability data, and selected user locale.
- Prompt templates are static code templates, but all deployment-specific values and feature flags come from environment variables.
- Requests use response schemas where possible so operational outputs are machine-readable.
- The backend validates Gemini outputs before returning them to clients or writing them to Firestore/BigQuery.
- Staff-only decision support must include confidence, assumptions, data freshness, and escalation guidance.

### 5.2 Core backend endpoints

| Endpoint | Audience | Purpose |
| --- | --- | --- |
| `GET /healthz` | Platform | Liveness/readiness check. |
| `GET /api/v1/config` | Frontend | Non-secret runtime configuration. |
| `POST /api/v1/assistant/chat` | Fans/staff | Multilingual Gemini assistant with grounded context. |
| `POST /api/v1/navigation/route` | Fans/volunteers | Stadium and venue route recommendations. |
| `POST /api/v1/accessibility/plan` | Fans/accessibility staff | Accessible route and assistance planning. |
| `POST /api/v1/transportation/options` | Fans/transport staff | Transit, walking, rideshare, shuttle, and accessible pickup recommendations. |
| `POST /api/v1/sustainability/advice` | Fans/ops | Waste, refill, low-carbon, and energy/crowd-aware guidance. |
| `POST /api/v1/crowd/recommendation` | Staff | Crowd pressure analysis and action suggestions. |
| `POST /api/v1/ops/decision-support` | Staff | Real-time operational decision support. |
| `POST /api/v1/ops/snapshot` | Scheduler/staff | Periodic operational snapshot generation. |

## 6. Frontend architecture

The frontend is a React PWA served by a lightweight Node server on Cloud Run. It must not embed environment-specific constants at build time. Runtime values are exposed through `/config.js`, generated by the server from environment variables.

```text
frontend/
  src/
    app/
    components/
    features/
      assistant/
      navigation/
      accessibility/
      transportation/
      sustainability/
      operations/
    i18n/
    services/
      apiClient.ts
      runtimeConfig.ts
    styles/
  server.js                 # Serves dist and runtime /config.js
  package.json
```

Frontend capabilities:

- Route planner with accessible and congestion-aware options.
- Multilingual assistant with visible data freshness and emergency disclaimers.
- Staff dashboard for heatmaps, incidents, snapshots, and recommended actions.
- Keyboard accessible, screen-reader friendly UI following WCAG 2.2 AA.
- Runtime-configured API base URL and Maps browser key.

## 7. Data model overview

Firestore collections should use environment-configurable names. Suggested defaults are shown for implementation consistency only.

| Collection | Purpose |
| --- | --- |
| `venues` | Venue metadata, gates, zones, amenities, accessibility features. |
| `venue_graphs` | Nodes and edges for internal stadium wayfinding. |
| `events` | Match schedule, expected attendance, staffing plans. |
| `crowd_zones` | Live/near-real-time zone density, queue status, ingress/egress status. |
| `incidents` | Operational incidents, severity, location, status, owner, timeline. |
| `assistant_sessions` | Minimal session metadata and safety/audit traces. Do not store secrets. |
| `ops_snapshots` | Generated decision-support summaries and data freshness metadata. |
| `sustainability_metrics` | Waste, refill, carbon, energy, and crowd-flow sustainability indicators. |

BigQuery stores append-only analytics tables for events, crowd observations, recommendations, assistant interactions, incident timelines, and sustainability metrics.

## 8. Security architecture

- Store API keys only in Secret Manager.
- Use separate service accounts for backend, frontend, and scheduler.
- Grant runtime service accounts only the permissions required by their component.
- Do not use or expose Gemini API keys. The frontend must call the backend for all Gemini interactions, and the backend must use ADC/IAM.
- The Maps browser key may be exposed to the browser only if restricted by HTTP referrer, API allowlist, and quota controls in Google Cloud Console.
- Enforce strict CORS using `ALLOWED_ORIGINS`; do not use wildcard origins in deployed environments.
- Validate all request bodies with Pydantic models.
- Rate-limit assistant and decision-support endpoints.
- Use structured logs and redact secrets, tokens, PII, and API keys.
- Require authentication and role checks for staff-only endpoints. Identity Platform, Firebase Auth, or an OIDC provider can be used; issuer, audience, and JWKS URL must be environment variables.
- Add secure headers in the frontend server and backend responses.
- Use dependency scanning and pinned dependency ranges.

## 9. Environment variable contract

### Backend runtime variables

| Variable | Required | Description |
| --- | --- | --- |
| `PROJECT_ID` | Yes | Google Cloud project ID. |
| `GCP_REGION` | Yes | Deployment region. |
| `ENVIRONMENT` | Yes | Environment name such as `dev`, `stage`, or `prod`. |
| `GEMINI_MODEL` | Yes | Gemini model, default deployment value should be `gemini-2.5-pro`. |
| `GEMINI_LOCATION` | Yes | Vertex AI Gemini location, default deployment value should be `global`. |
| `GEMINI_USE_VERTEX_AI` | Yes | Must be `true`; Gemini uses Vertex AI through ADC/IAM, not API keys. |
| `ALLOWED_ORIGINS` | Yes | Comma-separated frontend origins. No wildcard in deployed environments. |
| `FIRESTORE_DATABASE_ID` | Yes | Firestore database ID, commonly `(default)`. |
| `BIGQUERY_DATASET` | Yes | BigQuery dataset name. |
| `PUBSUB_TOPIC_OPERATIONS` | Yes | Operations topic name. |
| `PUBSUB_TOPIC_CROWD` | Yes | Crowd signal topic name. |
| `PUBSUB_TOPIC_SUSTAINABILITY` | Yes | Sustainability topic name. |
| `STAFF_AUTH_ISSUER` | No for local, Yes for prod | Staff auth token issuer. |
| `STAFF_AUTH_AUDIENCE` | No for local, Yes for prod | Staff auth token audience. |
| `STAFF_AUTH_JWKS_URL` | No for local, Yes for prod | Staff auth JWKS URL. |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Yes | Request limit for public endpoints. |
| `MAPS_API_SERVER_KEY_SECRET_NAME` | Optional | If server-side Maps APIs use a separate restricted key. |

### Frontend runtime variables

| Variable | Required | Description |
| --- | --- | --- |
| `ARENAFLOW_API_BASE_URL` | Yes | Backend Cloud Run URL or custom domain. |
| `ARENAFLOW_MAPS_BROWSER_API_KEY` | Yes for map UI | Restricted Maps browser API key. |
| `ARENAFLOW_DEFAULT_LOCALE` | Yes | Default locale such as `en`. |
| `ARENAFLOW_SUPPORTED_LOCALES` | Yes | Comma-separated locale list. |
| `ARENAFLOW_ENVIRONMENT` | Yes | Environment name. |

## 10. Deployment architecture

Deployment order:

1. Authenticate Google Cloud CLI and select the project.
2. Enable required APIs.
3. Create Artifact Registry repository.
4. Create backend, frontend, and scheduler service accounts.
5. Grant least-privilege IAM roles.
6. Create optional Maps Secret Manager secret only if browser Maps API keys are allowed; Gemini uses ADC/IAM and no API key secret.
7. Create Firestore database if needed.
8. Create Pub/Sub topics.
9. Create BigQuery dataset.
10. Build backend image remotely with Cloud Build and the pinned Python 3.12 Dockerfile, then deploy backend to Cloud Run.
11. Read backend URL.
12. Build frontend image remotely with Cloud Build and the pinned Node 20 Dockerfile, then deploy frontend to Cloud Run.
13. Read frontend URL.
14. Update backend CORS/runtime environment with the final frontend URL.
15. Create or update Cloud Scheduler operational snapshot job.
16. Validate health checks and service URLs.

The deployment specification and `deploy-arenaflow.ps1` follow this sequence.
