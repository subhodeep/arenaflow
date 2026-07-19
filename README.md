# ArenaFlow

ArenaFlow is a GenAI-enabled stadium operations and fan experience platform for FIFA World Cup 2026 venues. It helps fans, volunteers, venue staff, organizers, accessibility teams, transport coordinators, and sustainability teams with multilingual assistance, navigation, crowd management, accessibility planning, transportation guidance, sustainability recommendations, and operational intelligence.

The app uses:

- **Frontend:** React, TypeScript, Vite, Express runtime server
- **Backend:** Python, FastAPI, Pydantic
- **Cloud:** Google Cloud Run, Cloud Build, Artifact Registry, Firestore, Pub/Sub, BigQuery, Cloud Scheduler, Vertex AI Gemini
- **GenAI:** Gemini 2.5 Pro through **Vertex AI with Application Default Credentials**, not API keys

> Important: this project intentionally avoids Gemini API keys. Gemini access is handled by the backend Cloud Run service account using ADC/IAM.

---

## 1. Repository structure

```text
arenaflow/
  README.md
  architecture.md
  implementationspec.md
  deploymentspec.md
  deploy-arenaflow.ps1
  backend/
    Dockerfile
    runtime.txt
    requirements.txt
    Procfile
    app/
      main.py
      core/
      api/
      models/
      repositories/
      services/
    tests/
  frontend/
    Dockerfile
    .node-version
    package.json
    server.js
    index.html
    src/
      App.tsx
      components/
      features/
      i18n/
      services/
      styles/
```

---

## 2. High-level architecture

```text
React frontend on Cloud Run
        |
        | HTTPS
        v
FastAPI backend on Cloud Run
        |
        +--> Vertex AI Gemini 2.5 Pro by ADC/IAM
        +--> Firestore for venue, incident, crowd, route, and snapshot state
        +--> Pub/Sub for operational event streams
        +--> BigQuery for analytics and crowd trend queries
        +--> Cloud Scheduler for periodic operational snapshots
```

The frontend never calls Gemini directly. All GenAI calls go through the backend so secrets, IAM, prompts, grounding data, validation, and staff authorization stay server-side.

---

## 3. Main capabilities

ArenaFlow supports these app areas:

1. **Multilingual assistant** — fan/staff question answering grounded in venue context.
2. **Navigation** — stadium route guidance with accessibility and crowd-aware notes.
3. **Accessibility** — step-free, wheelchair, sensory, hearing, visual, companion, and assistance planning.
4. **Transportation** — public transit, shuttle, walking, accessible pickup, and post-match egress guidance.
5. **Sustainability** — refill, waste sorting, low-carbon route, energy, food, and crowd-aware sustainability nudges.
6. **Crowd management** — staff-only crowd recommendations.
7. **Operational intelligence** — staff-only decision support and scheduler-driven snapshots.

---

## 4. Authentication and API key policy

### Gemini

Gemini is accessed using:

- Vertex AI Gemini
- Cloud Run backend service account
- Application Default Credentials
- `roles/aiplatform.user`

No Gemini API key is required or used.

### Google Maps

The deployment supports `-SkipMapsSecret` for organizations that disallow API keys. If Maps browser API keys are also disallowed by your organization, deploy with:

```powershell
-SkipMapsSecret
```

The app still works, but browser map-specific UI/integration should remain disabled or limited.

---

## 5. Backend environment variables

The backend reads configuration from environment variables only.

| Variable | Purpose |
| --- | --- |
| `PROJECT_ID` | Google Cloud project ID. |
| `GCP_REGION` | Google Cloud region. |
| `ENVIRONMENT` | `local`, `dev`, `stage`, or `prod`. |
| `GEMINI_MODEL` | Gemini model, for example `gemini-2.5-pro`. |
| `GEMINI_LOCATION` | Vertex AI Gemini location. Deployment defaults to `global` for Gemini model availability. |
| `GEMINI_USE_VERTEX_AI` | Must be `true` for ADC/IAM Vertex AI access. |
| `ALLOWED_ORIGINS` | Comma-separated allowed frontend origins. Do not use `*` outside local/dev. |
| `FIRESTORE_DATABASE_ID` | Firestore database ID, usually `(default)`. |
| `BIGQUERY_DATASET` | BigQuery dataset name. |
| `PUBSUB_TOPIC_OPERATIONS` | Pub/Sub topic for operations events. |
| `PUBSUB_TOPIC_CROWD` | Pub/Sub topic for crowd signals. |
| `PUBSUB_TOPIC_SUSTAINABILITY` | Pub/Sub topic for sustainability events. |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Public endpoint request limit. |
| `STAFF_AUTH_ISSUER` | Staff JWT issuer for deployed staff auth. |
| `STAFF_AUTH_AUDIENCE` | Staff JWT audience. |
| `STAFF_AUTH_JWKS_URL` | Staff auth JWKS URL. |
| `ALLOW_LOCAL_STAFF_BYPASS` | Local-only staff bypass. Use only with `ENVIRONMENT=local`. |
| `SCHEDULER_SERVICE_ACCOUNT_EMAIL` | Scheduler service account email for snapshot invocation. |

---

## 6. Frontend environment variables

The frontend runtime server exposes non-secret config through `/config.js`.

| Variable | Purpose |
| --- | --- |
| `ARENAFLOW_API_BASE_URL` | Backend Cloud Run URL. |
| `ARENAFLOW_MAPS_BROWSER_API_KEY` | Optional restricted Maps browser key. Omit if keys are disallowed. |
| `ARENAFLOW_DEFAULT_LOCALE` | Default locale, for example `en`. |
| `ARENAFLOW_SUPPORTED_LOCALES` | Comma-separated locale list, for example `en,es,fr,pt`. |
| `ARENAFLOW_ENVIRONMENT` | Runtime environment. |
| `ARENAFLOW_DEFAULT_VENUE_ID` | Optional default venue ID shown in the frontend. |
| `ARENAFLOW_DEFAULT_EVENT_ID` | Optional default event ID. |

---

## 7. Local backend setup

From the repository root:

```powershell
cd C:\Subho\promptwars\arenaflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

Run the backend locally:

```powershell
cd backend
$env:ENVIRONMENT="local"
$env:PROJECT_ID=""
$env:GCP_REGION="us-central1"
$env:GEMINI_MODEL="gemini-2.5-pro"
$env:GEMINI_LOCATION="global"
$env:GEMINI_USE_VERTEX_AI="true"
$env:ALLOWED_ORIGINS="http://localhost:5173"
$env:FIRESTORE_DATABASE_ID="(default)"
$env:BIGQUERY_DATASET="arenaflow_local"
$env:PUBSUB_TOPIC_OPERATIONS="arenaflow-local-operations"
$env:PUBSUB_TOPIC_CROWD="arenaflow-local-crowd"
$env:PUBSUB_TOPIC_SUSTAINABILITY="arenaflow-local-sustainability"
$env:ALLOW_LOCAL_STAFF_BYPASS="true"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Local health check:

```powershell
Invoke-WebRequest http://localhost:8000/healthz -UseBasicParsing
```

Expected response:

```json
{
  "status": "ok",
  "app_name": "ArenaFlow",
  "app_version": "0.1.0",
  "environment": "local"
}
```

---

## 8. Local frontend setup

Install Node.js 20 first. Then:

```powershell
cd C:\Subho\promptwars\arenaflow\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The Vite dev server uses `/config.js` only when served by the production Express server. For local Vite testing, the frontend falls back to:

```text
ARENAFLOW_API_BASE_URL=http://localhost:8000
```

---

## 9. Running tests

Backend tests:

```powershell
cd C:\Subho\promptwars\arenaflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m pytest backend\tests
```

Expected result:

```text
5 passed
```

Frontend type/build check:

```powershell
cd C:\Subho\promptwars\arenaflow\frontend
npm install
npm run build
```

---

## 10. Deployment

Deployment is handled by:

```text
deploy-arenaflow.ps1
```

It uses Google Cloud CLI and Cloud Build remote Dockerfile builds. Docker is **not** required locally.

Recommended deployment command for an organization that disallows API keys:

```powershell
cd C:\Subho\promptwars\arenaflow
.\deploy-arenaflow.ps1 -ProjectId "YOUR_PROJECT_ID" -Region "us-central1" -FirestoreLocation "nam5" -BigQueryLocation "US" -SkipMapsSecret
```

The script runs these major steps:

1. Check local prerequisites
2. Prompt for optional Maps secret if needed
3. Enable required Google Cloud APIs
4. Create Artifact Registry repository
5. Create runtime service accounts
6. Grant project-level IAM permissions
7. Create optional Maps secret and secret version
8. Create Firestore database
9. Create Pub/Sub topics
10. Create BigQuery dataset
11. Build backend image remotely with Cloud Build Dockerfile
12. Deploy backend to Cloud Run
13. Build frontend image remotely with Cloud Build Dockerfile
14. Deploy frontend to Cloud Run
15. Finalize backend CORS with frontend URL
16. Grant scheduler invoker and configure token minting
17. Create or update Cloud Scheduler operational snapshot job
18. Validate deployed services

After successful deployment, the script prints:

```text
Backend:  https://...
Frontend: https://...
```

Open the frontend URL in your browser.

---

## 11. Getting deployed URLs later

Frontend URL:

```powershell
gcloud run services describe arenaflow-frontend --project "YOUR_PROJECT_ID" --region "us-central1" --format="value(status.url)"
```

Backend URL:

```powershell
gcloud run services describe arenaflow-backend --project "YOUR_PROJECT_ID" --region "us-central1" --format="value(status.url)"
```

Backend docs:

```text
https://YOUR_BACKEND_URL/docs
```

Backend config:

```text
https://YOUR_BACKEND_URL/api/v1/config
```

---

# 12. How to test each feature from the frontend

Open the deployed frontend URL, for example:

```text
https://arenaflow-frontend-xxxxx-uc.a.run.app
```

At the top of the app:

1. Choose a language.
2. Enter a **Venue ID**.

If you have not seeded real Firestore venue data yet, you can enter any non-empty venue ID such as:

```text
demo-venue
```

The backend is designed to degrade gracefully when Firestore, BigQuery, or Maps context is not found. Gemini responses will include assumptions and grounding summaries where available.

---

## 12.1 Test Multilingual Assistant

Frontend tab:

```text
Assistant
```

Steps:

1. Open the **Assistant** tab.
2. Set language to `EN` or another available locale.
3. Enter a venue ID, for example `demo-venue`.
4. In the question box, try:

```text
Where is the nearest accessible entrance and how do I avoid crowded areas?
```

5. Click **Ask ArenaFlow**.

Expected behavior:

- The app calls:

```text
POST /api/v1/assistant/chat
```

- You should see a polished, ChatGPT-style summary card with:
  - a main answer bubble
  - confidence and language badges
  - suggested next steps
  - assumptions
  - safety notes
  - data grounding
- If needed, expand **View technical response** to inspect the underlying JSON.

Suggested additional prompts:

```text
Can you explain waste sorting at the stadium in Spanish?
```

```text
How do I get from Gate A to Section 120 with step-free access?
```

```text
What should I do if I need sensory-sensitive support?
```

---

## 12.2 Test Navigation

The Navigation page includes a **keyless stadium wayfinding visualization**. It is not Google Maps and does not require a browser API key. It shows a stylized stadium floorplan with gates, section labels, crowd-pressure bands, transit areas, and a highlighted accessible route preview.

Frontend tab:

```text
Navigation
```

Steps:

1. Open the **Navigation** tab.
2. Enter a venue ID.
3. Set **Origin**, for example:

```text
Gate A
```

4. Set **Destination**, for example:

```text
Section 120
```

5. Click **Plan route**.

Expected behavior:

- The app calls:

```text
POST /api/v1/navigation/route
```

- You should see a polished route summary card with:
  - a main route recommendation
  - confidence and language badges
  - recommended route steps
  - accessibility and crowd notes where available
  - assumptions and safety notes
- If needed, expand **View technical response** to inspect the underlying JSON.

Notes:

- If `venue_graphs` data has not been seeded in Firestore, the backend returns a safe fallback route instruction.
- If Maps API keys are skipped, Google Maps rendering is not expected. The built-in stadium visualization still works because it is a secure SVG-based venue preview that does not depend on API keys.

---

## 12.3 Test Accessibility Planning

Frontend tab:

```text
Accessibility
```

Steps:

1. Open the **Accessibility** tab.
2. Enter a venue ID.
3. In **Needs**, try:

```text
wheelchair, step-free, low-sensory
```

4. Click **Create accessibility plan**.

Expected behavior:

- The app calls:

```text
POST /api/v1/accessibility/plan
```

- You should see a polished accessibility plan card with:
  - a main accessibility recommendation
  - assistance points
  - route steps where available
  - assumptions
  - safety notes
- If needed, expand **View technical response** to inspect the underlying JSON.

Try other needs:

```text
visual assistance, service animal, companion support
```

```text
hearing assistance, low-sensory route
```

---

## 12.4 Test Transportation Guidance

Frontend tab:

```text
Transportation
```

Steps:

1. Open the **Transportation** tab.
2. Enter a venue ID.
3. Set **Origin address**, for example:

```text
Downtown transit hub
```

4. Click **Find transportation**.

Expected behavior:

- The app calls:

```text
POST /api/v1/transportation/options
```

- You should see a polished transportation summary card with:
  - a main recommendation
  - transportation option cards
  - accessibility notes
  - carbon impact values where available
  - assumptions and safety notes
- If needed, expand **View technical response** to inspect the underlying JSON.

Try other origins:

```text
Airport terminal 1
```

```text
Main hotel district
```

```text
Accessible pickup zone north
```

---

## 12.5 Test Sustainability Guidance

Frontend tab:

```text
Sustainability
```

Steps:

1. Open the **Sustainability** tab.
2. Enter a venue ID.
3. Select an intent:
   - Water refill
   - Waste sorting
   - Low-carbon route
   - General
4. Click **Get sustainability advice**.

Expected behavior:

- The app calls:

```text
POST /api/v1/sustainability/advice
```

- You should see a polished sustainability advice card with:
  - a main recommendation
  - recommended actions
  - estimated impact where available
  - assumptions and safety notes
- If needed, expand **View technical response** to inspect the underlying JSON.

Suggested tests:

- Select **Water refill** and verify the recommendation discusses refill station behavior.
- Select **Waste sorting** and verify the recommendation discusses venue signage and waste streams.
- Select **Low-carbon route** and verify it suggests walking, transit, or shuttle options when safe.

---

## 12.6 Test Operations Dashboard

Frontend tab:

```text
Operations
```

This feature uses staff-only backend endpoints.

Endpoint called:

```text
POST /api/v1/ops/decision-support
```

### Local test option

For local testing only, start the backend with:

```powershell
$env:ENVIRONMENT="local"
$env:ALLOW_LOCAL_STAFF_BYPASS="true"
```

Then in the frontend Operations tab:

1. Leave **Staff token** empty.
2. Enter a situation such as:

```text
Gate B queues are increasing and accessible route access may be constrained.
```

3. Click **Generate decision support**.

Expected frontend output:

- a main operational recommendation
- priority/confidence metadata
- operational action cards
- escalation guidance
- alternatives
- assumptions and safety notes
- expandable **View technical response** JSON for reviewers

### Deployed test option

For deployed environments, configure staff JWT validation through these backend variables:

```text
STAFF_AUTH_ISSUER
STAFF_AUTH_AUDIENCE
STAFF_AUTH_JWKS_URL
```

The staff token must contain at least one of these roles or claims:

```text
arenaflow_staff
arenaflow_ops
arenaflow_admin
```

Then:

1. Paste a valid staff bearer token into **Staff token**.
2. Enter an operational situation.
3. Click **Generate decision support**.

If staff auth is not configured, this tab is expected to fail with an auth/configuration error. That is by design to avoid exposing operations endpoints publicly.

---

# 13. Direct API smoke tests

Replace `BACKEND_URL` with your backend Cloud Run URL.

Health:

```powershell
Invoke-WebRequest "$BACKEND_URL/healthz" -UseBasicParsing
```

Runtime config:

```powershell
Invoke-WebRequest "$BACKEND_URL/api/v1/config" -UseBasicParsing
```

Assistant:

```powershell
$body = @{
  venue_id = "demo-venue"
  language = "en"
  message = "How do I find an accessible entrance?"
  user_type = "fan"
} | ConvertTo-Json

Invoke-RestMethod "$BACKEND_URL/api/v1/assistant/chat" -Method Post -ContentType "application/json" -Body $body
```

Navigation:

```powershell
$body = @{
  venue_id = "demo-venue"
  language = "en"
  origin = "Gate A"
  destination = "Section 120"
  mobility_needs = @("step-free")
  avoid_crowds = $true
} | ConvertTo-Json

Invoke-RestMethod "$BACKEND_URL/api/v1/navigation/route" -Method Post -ContentType "application/json" -Body $body
```

---

# 14. Seeding data for richer tests

The app works without seeded data, but recommendations become much more grounded and impressive if Firestore contains venue context.

A repeatable demo seed script is included:

```text
scripts/seed_demo_data.py
```

It creates realistic hackathon demo data for:

- `venues/demo-venue`
- `events/demo-match`
- `crowd_zones`
- `incidents`
- `venue_graphs/demo-venue`
- `sustainability_metrics/demo-sustainability-current`

Seed the deployed Firestore database from your local machine:

```powershell
cd C:\Subho\promptwars\arenaflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install google-cloud-firestore
$env:PROJECT_ID="project-48f14331-7312-4357-ad6"
$env:FIRESTORE_DATABASE_ID="(default)"
python scripts\seed_demo_data.py
```

After seeding, use these values in the frontend:

```text
Venue ID: demo-venue
Event ID: demo-match
```

The current frontend displays Venue ID. Event ID is optional in the UI and backend requests can still ground on venue-level data. Direct API tests can include `event_id = "demo-match"`.

The seed data includes:

- accessible Gate A
- congested Gate C
- Section 120
- North Concourse step-free route
- refill stations
- first aid
- low-sensory room
- accessible pickup zone
- crowd pressure zones
- active incidents for elevator delay and Gate C pressure


---

# 15. Troubleshooting

## Frontend loads but API calls fail

Check `/config.js` from the frontend URL:

```text
https://YOUR_FRONTEND_URL/config.js
```

Confirm `ARENAFLOW_API_BASE_URL` points to the backend URL.

## Backend CORS errors

Confirm backend `ALLOWED_ORIGINS` contains the deployed frontend URL:

```powershell
gcloud run services describe arenaflow-backend --project "YOUR_PROJECT_ID" --region "us-central1"
```

## Operations dashboard fails

This is expected unless staff auth is configured or local bypass is enabled for local development.

## Gemini responses are generic

Check that:

- The backend service account has `roles/aiplatform.user`.
- Vertex AI API is enabled.
- `PROJECT_ID`, `GCP_REGION`, `GEMINI_MODEL`, `GEMINI_LOCATION=global`, and `GEMINI_USE_VERTEX_AI=true` are set.
- The selected model is available in the region.

## Maps are unavailable

If deployed with `-SkipMapsSecret`, browser Maps features are intentionally disabled or limited.

---

# 16. Security notes

- Gemini API keys are not used.
- The backend uses ADC/IAM for Gemini.
- Staff endpoints require JWT-based role authorization outside local bypass mode.
- Secrets are not logged.
- CORS must not use wildcard origins in production.
- The frontend renders model output as text/JSON, not raw HTML.
- Do not store staff tokens in localStorage.

---

# 17. Current deployment checklist

After deployment, verify:

- Frontend URL opens in a browser.
- Backend `/docs` opens in a browser.
- Backend `/api/v1/config` returns JSON.
- Assistant tab returns a response.
- Navigation tab returns route guidance.
- Accessibility tab returns a plan.
- Transportation tab returns options.
- Sustainability tab returns advice.
- Operations tab is locked down unless staff auth/local bypass is configured.
