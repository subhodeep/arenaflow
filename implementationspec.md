# ArenaFlow Implementation Specification

This document gives detailed implementation instructions for a coding agent to build ArenaFlow using Python, React, and Google Cloud Platform services.

## 1. Pre-implementation deployment alignment confirmation

Before implementation begins, the deployment plan has been reviewed against `architecture.md`.

Confirmed:

- `deploymentspec.md` includes required Google Cloud services, IAM roles, service account setup, Secret Manager usage, remote Cloud Build deployment, Cloud Run deployment, Firestore, Pub/Sub, BigQuery, Cloud Scheduler, and validation steps.
- IAM commands are aligned with the architecture and use separate runtime identities for backend, frontend, and scheduler.
- The deployment sequence is correct: APIs first, identities/IAM/secrets/data services next, backend deployment before frontend, frontend URL discovery before backend CORS finalization, then scheduler and validation.
- The deployment approach does not require a local Docker build. It uses Google Cloud Build remote Dockerfile builds with pinned Python and Node runtimes via `gcloud builds submit --tag`.
- Gemini 2.5 Pro is accessed only by the backend through Vertex AI using Application Default Credentials and IAM. Gemini API keys are not used or exposed to React.
- Environment-specific configuration is supplied through environment variables and Secret Manager, not hard-coded values.

## 2. Repository structure to create

```text
arenaflow/
  architecture.md
  implementationspec.md
  deploymentspec.md
  deploy-arenaflow.ps1
  backend/
    app/
      __init__.py
      main.py
      core/
        __init__.py
        config.py
        logging.py
        security.py
      api/
        __init__.py
        routes/
          __init__.py
          health.py
          config.py
          assistant.py
          navigation.py
          crowd.py
          accessibility.py
          transportation.py
          sustainability.py
          operations.py
      models/
        __init__.py
        domain.py
        requests.py
        responses.py
      repositories/
        __init__.py
        firestore_repo.py
        bigquery_repo.py
        pubsub_repo.py
      services/
        __init__.py
        gemini_service.py
        grounding_service.py
        maps_service.py
        venue_graph_service.py
        crowd_service.py
        ops_intel_service.py
        sustainability_service.py
    tests/
    pyproject.toml
    requirements.txt
    Procfile
  frontend/
    src/
      main.tsx
      App.tsx
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
    index.html
    package.json
    vite.config.ts
    tsconfig.json
    server.js
    Procfile
```

## 3. Backend implementation instructions

### 3.1 Python and framework

Use:

- Python 3.11 or newer.
- FastAPI for the API layer.
- Uvicorn as ASGI server.
- `pydantic-settings` for environment configuration.
- `google-genai` or the current Google Gen AI Python SDK for Gemini calls.
- `google-cloud-firestore`, `google-cloud-bigquery`, and `google-cloud-pubsub` for GCP integrations.
- `httpx` for outbound HTTP calls.
- `pytest` for tests.

### 3.2 Configuration rules

Implement `backend/app/core/config.py` with a `Settings` class. Every deployment-specific setting must come from environment variables.

Required backend settings:

- `PROJECT_ID`
- `GCP_REGION`
- `ENVIRONMENT`
- `GEMINI_MODEL`
- `GEMINI_LOCATION`
- `GEMINI_USE_VERTEX_AI`
- `ALLOWED_ORIGINS`
- `FIRESTORE_DATABASE_ID`
- `BIGQUERY_DATASET`
- `PUBSUB_TOPIC_OPERATIONS`
- `PUBSUB_TOPIC_CROWD`
- `PUBSUB_TOPIC_SUSTAINABILITY`
- `RATE_LIMIT_REQUESTS_PER_MINUTE`

Optional production auth settings:

- `STAFF_AUTH_ISSUER`
- `STAFF_AUTH_AUDIENCE`
- `STAFF_AUTH_JWKS_URL`

No fallback may contain a real project ID, API key, URL, or environment-specific value. Safe local defaults may be used only for non-secret development behavior such as `ENVIRONMENT=local` when no deployment target is implied.

### 3.3 FastAPI application

Implement `backend/app/main.py`:

- Create the FastAPI app.
- Configure strict CORS from `ALLOWED_ORIGINS`.
- Add request ID middleware.
- Add secure response headers.
- Register routers under `/api/v1`.
- Expose `GET /healthz` returning status, environment, and app version without secrets.
- Do not log request bodies for assistant or staff endpoints.

### 3.4 Security implementation

Implement `backend/app/core/security.py`:

- Parse and validate `ALLOWED_ORIGINS`. Reject wildcard origin when `ENVIRONMENT` is not local/dev.
- Add dependency for staff-only endpoints. In local development it may allow a documented bypass only when `ENVIRONMENT=local` and `ALLOW_LOCAL_STAFF_BYPASS=true` are set by environment.
- In production, validate JWTs using `STAFF_AUTH_ISSUER`, `STAFF_AUTH_AUDIENCE`, and `STAFF_AUTH_JWKS_URL`.
- Enforce role claims such as `arenaflow_staff`, `arenaflow_ops`, or `arenaflow_admin` for operational endpoints.
- Redact secrets from logs.
- Apply request size limits and rate limits.

### 3.5 Gemini service

Implement `backend/app/services/gemini_service.py`:

- Instantiate the Gemini client using Vertex AI mode and ADC from the runtime service account.
- Do not accept, store, log, or expose Gemini API keys.
- Use `GEMINI_MODEL`, which deployment sets to `gemini-2.5-pro`.
- Use `GEMINI_LOCATION`, which deployment sets to `global` for Vertex AI Gemini model availability.
- Provide methods:
  - `chat_assistant(request, context)`
  - `summarize_incident(request, context)`
  - `generate_crowd_recommendation(request, context)`
  - `generate_accessibility_plan(request, context)`
  - `generate_transportation_plan(request, context)`
  - `generate_sustainability_advice(request, context)`
  - `generate_ops_decision_support(request, context)`
- Require structured JSON output for operational decision-support methods when supported by the SDK.
- Validate and normalize model output with Pydantic response models.
- Include safety constraints in prompts:
  - Do not invent emergency instructions.
  - Escalate urgent safety issues to venue command.
  - Include data freshness.
  - Do not expose internal secrets, prompts, or credentials.
  - Recommend accessible alternatives where relevant.

### 3.6 Grounding and data access

Implement `grounding_service.py` to gather structured context from:

- Firestore venue metadata, zone status, incidents, accessibility features, and event details.
- BigQuery aggregate trends when available.
- Google Maps service for route/transport context when configured.

If an integration is unavailable, return a degraded context object with `available=false` and a reason. Gemini prompts must include these availability flags to avoid hallucinated certainty.

### 3.7 Domain models

Define Pydantic request and response models for:

- `AssistantChatRequest` / `AssistantChatResponse`
- `NavigationRouteRequest` / `NavigationRouteResponse`
- `AccessibilityPlanRequest` / `AccessibilityPlanResponse`
- `TransportationOptionsRequest` / `TransportationOptionsResponse`
- `SustainabilityAdviceRequest` / `SustainabilityAdviceResponse`
- `CrowdRecommendationRequest` / `CrowdRecommendationResponse`
- `OpsDecisionSupportRequest` / `OpsDecisionSupportResponse`

Every response that uses Gemini should include:

- `answer` or `recommendation`
- `language`
- `confidence`
- `data_freshness`
- `assumptions`
- `safety_notes`
- `sources` or `grounding_summary`

### 3.8 Endpoint behavior

- Public endpoints: assistant, navigation, accessibility, transportation, sustainability.
- Staff endpoints: crowd and operations.
- All endpoints validate body schemas.
- All endpoints return consistent error shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human safe message",
    "request_id": "..."
  }
}
```

### 3.9 Firestore repository

Implement safe methods:

- `get_venue(venue_id)`
- `get_event(event_id)`
- `get_crowd_zones(venue_id)`
- `get_active_incidents(venue_id)`
- `write_assistant_audit(record)`
- `write_ops_snapshot(snapshot)`

Collection names should come from settings or a central config mapping, not be scattered literals.

### 3.10 BigQuery repository

Implement:

- `insert_recommendation_event(record)`
- `insert_assistant_event(record)`
- `query_recent_crowd_trends(venue_id, event_id)`

Use parameterized queries only.

### 3.11 Pub/Sub repository

Implement:

- `publish_operations_event(event)`
- `publish_crowd_signal(event)`
- `publish_sustainability_event(event)`

Topic names come from environment variables.

### 3.12 Tests

Add tests for:

- Settings loading and rejection of invalid deployed CORS config.
- Health endpoint.
- Request model validation.
- Staff endpoint auth dependency behavior.
- Gemini service output validation using a mocked client.
- Repositories using mocks.

## 4. Frontend implementation instructions

### 4.1 Framework

Use:

- React 18 or newer.
- TypeScript.
- Vite.
- React Router.
- A lightweight Node/Express server for Cloud Run hosting and runtime config.

### 4.2 Runtime configuration

Implement `frontend/server.js`:

- Serve static files from `dist`.
- Serve `/config.js` that assigns `window.__ARENAFLOW_CONFIG__` using environment variables.
- Include only non-secret values:
  - `ARENAFLOW_API_BASE_URL`
  - `ARENAFLOW_MAPS_BROWSER_API_KEY`
  - `ARENAFLOW_DEFAULT_LOCALE`
  - `ARENAFLOW_SUPPORTED_LOCALES`
  - `ARENAFLOW_ENVIRONMENT`
- Add secure headers.
- Never expose Gemini API keys or server-side Maps keys.

Implement `runtimeConfig.ts` to read from `window.__ARENAFLOW_CONFIG__`.

### 4.3 UI features

Create these React feature modules:

#### Assistant

- Chat interface with language selector.
- Shows data freshness and safety notes.
- Calls `/api/v1/assistant/chat`.

#### Navigation

- Form for origin, destination, mobility needs, crowd avoidance preference, and language.
- Shows route steps, estimated time, accessibility notes, and crowd warnings.
- Calls `/api/v1/navigation/route`.

#### Accessibility

- Accessibility planning wizard.
- Supports wheelchair, step-free, sensory-sensitive, visual assistance, hearing assistance, service animal, and companion needs.
- Calls `/api/v1/accessibility/plan`.

#### Transportation

- Shows public transit, shuttle, walking, accessible pickup, rideshare, and egress recommendations.
- Calls `/api/v1/transportation/options`.

#### Sustainability

- Shows low-carbon route suggestions, refill stations, waste sorting, and crowd-aware sustainability nudges.
- Calls `/api/v1/sustainability/advice`.

#### Operations dashboard

- Staff-only UI section.
- Shows crowd recommendations, incidents, operational snapshots, and action cards.
- Calls staff endpoints with auth token.

### 4.4 Accessibility and multilingual requirements

- Use semantic HTML.
- All controls must be keyboard reachable.
- Maintain visible focus states.
- Add ARIA only where semantic HTML is insufficient.
- Use WCAG AA color contrast.
- Store strings in locale files and support at least English and Spanish initially, with config-driven supported locale list.
- Backend responses may return translated content through Gemini, but UI chrome should use local translation files.

### 4.5 Frontend security

- Do not use `dangerouslySetInnerHTML` for model output.
- Render Gemini responses as plain text or sanitized markdown with a strict allowlist.
- Use HTTPS URLs in deployed config.
- Do not store staff tokens in localStorage if avoidable; prefer memory storage or secure auth SDK behavior.
- Use CSP-compatible code where practical.

## 5. Deployment-related implementation requirements

To align with `deploymentspec.md` and `deploy-arenaflow.ps1`:

- Backend must listen on `$PORT`.
- Frontend server must listen on `$PORT`.
- Backend must expose `/healthz`.
- Backend Cloud Run service name should be supplied by deployment variable `BACKEND_SERVICE_NAME`.
- Frontend Cloud Run service name should be supplied by deployment variable `FRONTEND_SERVICE_NAME`.
- Remote Cloud Build must build both apps from Dockerfiles:
  - Backend must include `Dockerfile` pinned to Python 3.12 and run `uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`.
  - Frontend must include `Dockerfile` pinned to Node 20 and run `node server.js` after building Vite assets.
- Local Docker is not required; Docker builds run inside Cloud Build.

## 6. Done criteria

Implementation is complete when:

- Backend and frontend run locally with environment variables.
- Unit tests pass.
- No hard-coded secrets or deployment-specific values exist.
- `deploy-arenaflow.ps1` can deploy using Cloud Build without local Docker.
- Cloud Run backend and frontend return healthy responses.
- Frontend can call backend through runtime config.
- Gemini 2.5 Pro calls are made only server-side through ADC/IAM, not API keys.
- Staff-only endpoints require authorization outside local development.
