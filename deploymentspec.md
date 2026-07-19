# ArenaFlow Google Cloud Deployment Specification

This specification deploys ArenaFlow to Google Cloud Platform from a Windows machine using Google Cloud CLI. It does not require local Docker builds. Backend and frontend images are built remotely by Cloud Build using Dockerfiles with pinned Python and Node runtimes.

## 1. Deployment alignment verification

This deployment specification has been reviewed against `architecture.md` and `implementationspec.md`.

Confirmed alignment:

- The architecture uses Cloud Run, Cloud Build, Artifact Registry, Secret Manager for the optional Maps browser key, Firestore, Pub/Sub, BigQuery, Cloud Scheduler, Cloud Logging/Monitoring, Google Maps Platform APIs, and Gemini 2.5 Pro on Vertex AI.
- The deployment sequence creates foundational cloud resources before deploying application services.
- Separate service accounts are used for backend runtime, frontend runtime, and scheduler invocation.
- Gemini access is server-side only and uses Application Default Credentials through the backend Cloud Run service account. No Gemini API key is created, stored, mounted, or exposed.
- Frontend runtime configuration is injected through environment variables and `/config.js`; no environment-specific constants are hard-coded into React build artifacts.
- The Maps browser key can be made available to the frontend service as an environment secret, but it must be restricted in Google Cloud Console by HTTP referrer, allowed APIs, and quota.
- IAM grants are component-specific. Runtime service accounts do not receive broad owner/editor roles.
- The local machine needs Google Cloud CLI and the `gcloud`/`bq` commands, but does not need Docker.

## 2. Local prerequisites

Install and configure:

1. Google Cloud CLI for Windows.
2. PowerShell 7+ is recommended, but Windows PowerShell 5.1 can also run the generated script.
3. A Google Cloud project with billing enabled.
4. Organization policy allowing service account ADC access to Vertex AI Gemini.
5. A Google Maps Platform browser key if map UI features are enabled. If API keys are fully disallowed, run deployment with `-SkipMapsSecret` and disable browser map features.
6. Source directories `backend/` and `frontend/` following `implementationspec.md`.

Authenticate locally:

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project "YOUR_PROJECT_ID"
```

If authentication opens a browser, run the command directly from your terminal.

## 3. Required deployer permissions

The account running deployment needs permissions to enable services, create service accounts, grant IAM, create secrets, create data services, build images, deploy Cloud Run services, and create scheduler jobs.

For a tightly managed organization, ask a project administrator to grant these roles temporarily to the deployer account:

```powershell
$PROJECT_ID="YOUR_PROJECT_ID"
$DEPLOYER="user:you@example.com"

$ROLES=@(
  "roles/serviceusage.serviceUsageAdmin",
  "roles/iam.serviceAccountAdmin",
  "roles/resourcemanager.projectIamAdmin",
  "roles/artifactregistry.admin",
  "roles/cloudbuild.builds.editor",
  "roles/run.admin",
  "roles/iam.serviceAccountUser",
  "roles/secretmanager.admin",
  "roles/aiplatform.admin",
  "roles/datastore.owner",
  "roles/pubsub.admin",
  "roles/bigquery.admin",
  "roles/cloudscheduler.admin",
  "roles/logging.viewer",
  "roles/monitoring.viewer"
)

foreach ($ROLE in $ROLES) {
  gcloud projects add-iam-policy-binding $PROJECT_ID --member=$DEPLOYER --role=$ROLE
}
```

For a hackathon or sandbox project, a project Owner can run deployment directly, but Owner should not be used as an application runtime role.

## 4. Google Cloud APIs to enable

Enable these APIs:

```powershell
gcloud services enable serviceusage.googleapis.com --project=$PROJECT_ID
gcloud services enable `
  cloudresourcemanager.googleapis.com `
  iam.googleapis.com `
  run.googleapis.com `
  cloudbuild.googleapis.com `
  artifactregistry.googleapis.com `
  secretmanager.googleapis.com `
  firestore.googleapis.com `
  pubsub.googleapis.com `
  bigquery.googleapis.com `
  cloudscheduler.googleapis.com `
  logging.googleapis.com `
  monitoring.googleapis.com `
  aiplatform.googleapis.com `
  generativelanguage.googleapis.com `
  apikeys.googleapis.com `
  maps-backend.googleapis.com `
  routes.googleapis.com `
  places.googleapis.com `
  geocoding-backend.googleapis.com `
  --project=$PROJECT_ID
```

## 5. Resource naming variables

Recommended deployment variables:

| Variable | Example | Purpose |
| --- | --- | --- |
| `PROJECT_ID` | `my-arenaflow-project` | Google Cloud project. |
| `REGION` | `us-central1` | Cloud Run, Artifact Registry, Scheduler region. |
| `FIRESTORE_LOCATION` | `nam5` | Firestore multi-region or regional location. |
| `BIGQUERY_LOCATION` | `US` | BigQuery dataset location. |
| `ENVIRONMENT` | `dev` | Runtime environment. |
| `ARTIFACT_REPO` | `arenaflow` | Docker repository in Artifact Registry. |
| `BACKEND_SERVICE_NAME` | `arenaflow-backend` | Backend Cloud Run service. |
| `FRONTEND_SERVICE_NAME` | `arenaflow-frontend` | Frontend Cloud Run service. |
| `BACKEND_SA_NAME` | `arenaflow-backend-sa` | Backend runtime identity. |
| `FRONTEND_SA_NAME` | `arenaflow-frontend-sa` | Frontend runtime identity. |
| `SCHEDULER_SA_NAME` | `arenaflow-scheduler-sa` | Scheduler OIDC identity. |
| `MAPS_SECRET_NAME` | `arenaflow-maps-browser-api-key` | Optional Maps browser key secret. Skip if API keys are disallowed. |
| `FIRESTORE_DATABASE_ID` | `(default)` | Firestore database. |
| `BIGQUERY_DATASET` | `arenaflow_ops` | Analytics dataset. |
| `PUBSUB_TOPIC_OPERATIONS` | `arenaflow-operations-events` | Operations events. |
| `PUBSUB_TOPIC_CROWD` | `arenaflow-crowd-signals` | Crowd signals. |
| `PUBSUB_TOPIC_SUSTAINABILITY` | `arenaflow-sustainability-events` | Sustainability events. |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Required Gemini model. |

## 6. Service accounts

Create runtime service accounts:

```powershell
gcloud iam service-accounts create $BACKEND_SA_NAME --display-name="ArenaFlow backend runtime" --project=$PROJECT_ID
gcloud iam service-accounts create $FRONTEND_SA_NAME --display-name="ArenaFlow frontend runtime" --project=$PROJECT_ID
gcloud iam service-accounts create $SCHEDULER_SA_NAME --display-name="ArenaFlow scheduler invoker" --project=$PROJECT_ID

$BACKEND_SA="$BACKEND_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$FRONTEND_SA="$FRONTEND_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$SCHEDULER_SA="$SCHEDULER_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
```

## 7. Runtime IAM grants

### 7.1 Backend service account

The backend reads/writes Firestore, publishes Pub/Sub messages, reads/writes BigQuery analytics, and calls Gemini 2.5 Pro on Vertex AI using ADC.

```powershell
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BACKEND_SA" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BACKEND_SA" --role="roles/pubsub.publisher"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BACKEND_SA" --role="roles/bigquery.jobUser"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BACKEND_SA" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BACKEND_SA" --role="roles/aiplatform.user"
```

Note: dataset-level `bq add-iam-policy-binding` is intentionally not used by the script because some organizations require allowlisting for that feature. Project-level `roles/bigquery.dataEditor` is less restrictive than dataset-level IAM, but it is more broadly supported for this deployment path.

### 7.2 Frontend service account

The frontend only needs to read the Maps browser key secret if map UI is enabled.

```powershell
gcloud secrets add-iam-policy-binding $MAPS_SECRET_NAME --project=$PROJECT_ID --member="serviceAccount:$FRONTEND_SA" --role="roles/secretmanager.secretAccessor"
```

### 7.3 Scheduler service account

The scheduler invokes the backend snapshot endpoint with an OIDC token.

```powershell
gcloud run services add-iam-policy-binding $BACKEND_SERVICE_NAME `
  --project=$PROJECT_ID `
  --region=$REGION `
  --member="serviceAccount:$SCHEDULER_SA" `
  --role="roles/run.invoker"
```

If Cloud Scheduler cannot mint OIDC tokens for the scheduler service account, grant the Cloud Scheduler service agent token creator permission:

```powershell
$PROJECT_NUMBER=(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
$SCHEDULER_SERVICE_AGENT="service-$PROJECT_NUMBER@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
gcloud iam service-accounts add-iam-policy-binding $SCHEDULER_SA `
  --project=$PROJECT_ID `
  --member="serviceAccount:$SCHEDULER_SERVICE_AGENT" `
  --role="roles/iam.serviceAccountTokenCreator"
```

### 7.4 Cloud Build image push permission

Cloud Build must be able to push images to Artifact Registry.

```powershell
$PROJECT_NUMBER=(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
$CLOUD_BUILD_SA="$PROJECT_NUMBER@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$CLOUD_BUILD_SA" --role="roles/artifactregistry.writer"
```

## 8. Artifact Registry

Create the Docker repository:

```powershell
gcloud artifacts repositories create $ARTIFACT_REPO `
  --project=$PROJECT_ID `
  --repository-format=docker `
  --location=$REGION `
  --description="ArenaFlow container images"
```

## 9. Optional Maps browser key secret

Gemini does not use an API key. It uses ADC through the backend Cloud Run service account and `roles/aiplatform.user`.

If your organization's policy disallows all API keys, skip this section and deploy with `-SkipMapsSecret`. If browser map features are allowed to use a restricted Maps browser key, create only the Maps secret:

```powershell
gcloud secrets create $MAPS_SECRET_NAME --project=$PROJECT_ID --replication-policy=automatic
$MAPS_BROWSER_API_KEY | gcloud secrets versions add $MAPS_SECRET_NAME --project=$PROJECT_ID --data-file=-
gcloud secrets add-iam-policy-binding $MAPS_SECRET_NAME --project=$PROJECT_ID --member="serviceAccount:$FRONTEND_SA" --role="roles/secretmanager.secretAccessor"
```

Security requirement for the Maps browser key if used:

- Restrict by HTTP referrer to the final frontend domain.
- Restrict allowed APIs to only the Maps APIs the frontend uses.
- Set quotas and alerting.
- Rotate if exposed in logs or source control.

## 10. Firestore

Create Firestore Native database if it does not already exist:

```powershell
gcloud firestore databases create `
  --project=$PROJECT_ID `
  --database=$FIRESTORE_DATABASE_ID `
  --location=$FIRESTORE_LOCATION `
  --type=firestore-native
```

For many projects the default database can be created only once. If it already exists, skip creation.

## 11. Pub/Sub topics

```powershell
gcloud pubsub topics create $PUBSUB_TOPIC_OPERATIONS --project=$PROJECT_ID
gcloud pubsub topics create $PUBSUB_TOPIC_CROWD --project=$PROJECT_ID
gcloud pubsub topics create $PUBSUB_TOPIC_SUSTAINABILITY --project=$PROJECT_ID
```

## 12. BigQuery dataset

```powershell
bq --location=$BIGQUERY_LOCATION mk --dataset "$PROJECT_ID:$BIGQUERY_DATASET"
```

The backend service account receives project-level `roles/bigquery.jobUser` and `roles/bigquery.dataEditor` in the IAM step. Application migrations or seed scripts should create tables. If using BigQuery automatic schema from inserts, still validate schemas in application code.

## 13. Remote build and deploy backend

Build backend remotely with Cloud Build using `backend/Dockerfile`, which pins Python 3.12:

```powershell
$IMAGE_TAG=(Get-Date -Format "yyyyMMddHHmmss")
$BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/$BACKEND_SERVICE_NAME:$IMAGE_TAG"

gcloud builds submit .\backend `
  --project=$PROJECT_ID `
  --tag=$BACKEND_IMAGE
```

Deploy backend to Cloud Run:

```powershell
gcloud run deploy $BACKEND_SERVICE_NAME `
  --project=$PROJECT_ID `
  --region=$REGION `
  --image=$BACKEND_IMAGE `
  --service-account=$BACKEND_SA `
  --allow-unauthenticated `
  --min-instances=0 `
  --max-instances=10 `
  --set-env-vars="PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,ENVIRONMENT=$ENVIRONMENT,GEMINI_MODEL=$GEMINI_MODEL,GEMINI_USE_VERTEX_AI=true,ALLOWED_ORIGINS=http://localhost:5173,FIRESTORE_DATABASE_ID=$FIRESTORE_DATABASE_ID,BIGQUERY_DATASET=$BIGQUERY_DATASET,PUBSUB_TOPIC_OPERATIONS=$PUBSUB_TOPIC_OPERATIONS,PUBSUB_TOPIC_CROWD=$PUBSUB_TOPIC_CROWD,PUBSUB_TOPIC_SUSTAINABILITY=$PUBSUB_TOPIC_SUSTAINABILITY,RATE_LIMIT_REQUESTS_PER_MINUTE=60,SCHEDULER_SERVICE_ACCOUNT_EMAIL=$SCHEDULER_SA"
```

The backend is deployed with temporary local CORS first because the frontend URL is unknown until the frontend service is deployed.

Get the backend URL:

```powershell
$BACKEND_URL=(gcloud run services describe $BACKEND_SERVICE_NAME --project=$PROJECT_ID --region=$REGION --format="value(status.url)")
```

## 14. Remote build and deploy frontend

Build frontend remotely with Cloud Build using `frontend/Dockerfile`, which pins Node 20:

```powershell
$FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/$FRONTEND_SERVICE_NAME:$IMAGE_TAG"

gcloud builds submit .\frontend `
  --project=$PROJECT_ID `
  --tag=$FRONTEND_IMAGE
```

Deploy frontend to Cloud Run. This command uses gcloud's custom delimiter syntax (`^~^`) because `ARENAFLOW_SUPPORTED_LOCALES` contains commas:

```powershell
gcloud run deploy $FRONTEND_SERVICE_NAME `
  --project=$PROJECT_ID `
  --region=$REGION `
  --image=$FRONTEND_IMAGE `
  --service-account=$FRONTEND_SA `
  --allow-unauthenticated `
  --min-instances=0 `
  --max-instances=10 `
  --set-env-vars="^~^ARENAFLOW_API_BASE_URL=$BACKEND_URL~ARENAFLOW_DEFAULT_LOCALE=en~ARENAFLOW_SUPPORTED_LOCALES=en,es,fr,pt~ARENAFLOW_ENVIRONMENT=$ENVIRONMENT" `
  --set-secrets="ARENAFLOW_MAPS_BROWSER_API_KEY=$MAPS_SECRET_NAME:latest"
```

Get the frontend URL:

```powershell
$FRONTEND_URL=(gcloud run services describe $FRONTEND_SERVICE_NAME --project=$PROJECT_ID --region=$REGION --format="value(status.url)")
```

## 15. Finalize backend CORS

Update the backend with the final frontend URL:

```powershell
gcloud run services update $BACKEND_SERVICE_NAME `
  --project=$PROJECT_ID `
  --region=$REGION `
  --update-env-vars="ALLOWED_ORIGINS=$FRONTEND_URL"
```

If you also use localhost for testing, set `ALLOWED_ORIGINS` to a comma-separated value such as:

```text
https://frontend-url.run.app,http://localhost:5173
```

Do not use `*` in deployed environments.

## 16. Cloud Scheduler operational snapshot job

Create a scheduler job that calls the backend snapshot endpoint.

```powershell
$SNAPSHOT_URI="$BACKEND_URL/api/v1/ops/snapshot"
$SCHEDULER_JOB_NAME="arenaflow-ops-snapshot"

if (gcloud scheduler jobs describe $SCHEDULER_JOB_NAME --project=$PROJECT_ID --location=$REGION 2>$null) {
  gcloud scheduler jobs update http $SCHEDULER_JOB_NAME `
    --project=$PROJECT_ID `
    --location=$REGION `
    --schedule="*/5 * * * *" `
    --uri=$SNAPSHOT_URI `
    --http-method=POST `
    --oidc-service-account-email=$SCHEDULER_SA `
    --oidc-token-audience=$BACKEND_URL `
    --headers="Content-Type=application/json" `
    --message-body='{"source":"cloud-scheduler"}'
} else {
  gcloud scheduler jobs create http $SCHEDULER_JOB_NAME `
    --project=$PROJECT_ID `
    --location=$REGION `
    --schedule="*/5 * * * *" `
    --uri=$SNAPSHOT_URI `
    --http-method=POST `
    --oidc-service-account-email=$SCHEDULER_SA `
    --oidc-token-audience=$BACKEND_URL `
    --headers="Content-Type=application/json" `
    --message-body='{"source":"cloud-scheduler"}'
}
```

The backend must validate scheduler OIDC tokens or otherwise restrict this endpoint at the application layer because the backend Cloud Run service is publicly reachable for fan endpoints.

## 17. Validation

Validate deployment:

```powershell
Write-Host "Backend: $BACKEND_URL"
Write-Host "Frontend: $FRONTEND_URL"

Invoke-WebRequest "$BACKEND_URL/healthz" -UseBasicParsing
Invoke-WebRequest "$FRONTEND_URL" -UseBasicParsing
Invoke-WebRequest "$FRONTEND_URL/config.js" -UseBasicParsing

gcloud run services describe $BACKEND_SERVICE_NAME --project=$PROJECT_ID --region=$REGION
gcloud run services describe $FRONTEND_SERVICE_NAME --project=$PROJECT_ID --region=$REGION
```

Check logs:

```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$BACKEND_SERVICE_NAME" --project=$PROJECT_ID --limit=50 --format=json
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$FRONTEND_SERVICE_NAME" --project=$PROJECT_ID --limit=50 --format=json
```

## 18. Deployment script

The generated script `deploy-arenaflow.ps1` implements this sequence with clear step logging and pause-before-step behavior by default. It uses Cloud Build remote Dockerfile builds and does not call local `docker build`.

Example with interactive secret prompts:

```powershell
.\deploy-arenaflow.ps1 `
  -ProjectId "YOUR_PROJECT_ID" `
  -Region "us-central1" `
  -FirestoreLocation "nam5" `
  -BigQueryLocation "US"
```

Example passing secrets as PowerShell `SecureString` values:

```powershell
$gemini = ConvertTo-SecureString "YOUR_GEMINI_KEY" -AsPlainText -Force
$maps = ConvertTo-SecureString "YOUR_RESTRICTED_MAPS_BROWSER_KEY" -AsPlainText -Force

.\deploy-arenaflow.ps1 `
  -ProjectId "YOUR_PROJECT_ID" `
  -GeminiApiKey $gemini `
  -MapsBrowserApiKey $maps
```

To run without prompts between steps:

```powershell
.\deploy-arenaflow.ps1 -ProjectId "YOUR_PROJECT_ID" -GeminiApiKey $gemini -MapsBrowserApiKey $maps -AutoApprove
```

## 19. Post-deployment security checklist

- Restrict Maps browser key to the final frontend URL.
- Rotate any key accidentally pasted into logs or terminals shared with others.
- Replace local/dev staff bypass settings before production.
- Configure staff identity provider variables before exposing staff dashboards.
- Confirm Cloud Run backend has no wildcard CORS.
- Confirm secrets are not visible in Cloud Run logs.
- Set alerting on high Gemini errors, high latency, quota errors, and 5xx rates.
- Review IAM bindings and remove temporary deployer permissions if they were granted for deployment only.
