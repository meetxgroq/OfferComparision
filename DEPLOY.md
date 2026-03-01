# BenchMarked – Deployment Guide

This doc covers deploying the app for production (Vercel + Cloud Run + Supabase + Gemini). For local setup see [SETUP_GUIDE.md](SETUP_GUIDE.md) and [.env.example](.env.example).

---

## Deploy Cloud Run right now (step-by-step)

**Do you need to commit, push, and clone?** It depends **where** you run the deploy command:

| Where you run `gcloud run deploy --source .` | Need to push & clone? |
|---------------------------------------------|------------------------|
| **Your laptop** (with gcloud CLI installed)   | **No.** Run from your repo folder. The CLI uploads that folder to Cloud Build. |
| **Google Cloud Shell** (browser)            | **Yes.** Cloud Shell has no copy of your code. Push to GitHub, then clone the repo in Cloud Shell and run deploy from the cloned folder. |

### Option A: Deploy from your laptop

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and run `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`.
2. In a terminal, go to your **repo root** (the folder that contains `Dockerfile`, `api_server.py`, `requirements.txt`):
   ```bash
   cd /path/to/OfferComparision
   ```
3. Follow **Step 3** below (create secrets, then run the deploy command from this folder). No commit/push or clone needed.

### Option B: Deploy from Google Cloud Shell

1. **Commit and push** your code to GitHub (so Cloud Shell can clone it):
   ```bash
   git add .
   git commit -m "Deploy to Cloud Run"
   git push origin main
   ```
2. Open [Google Cloud Console](https://console.cloud.google.com/) → select your project → click **Activate Cloud Shell** (terminal icon in the top bar).
3. **Clone the repo** and go into it:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```
   (Use your real GitHub URL; if the repo is private, use a personal access token or SSH.)
4. In Cloud Shell you are already authenticated. Set region and enable APIs (see Step 3 below), create secrets, then run the **deploy** command from this cloned folder (`--source .` will use the current directory).

### Order of steps (same for A or B)

1. Have a GCP project with billing enabled.
2. Set region: `gcloud config set run/region us-central1`
3. Enable APIs: `gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com`
4. Create the four secrets in Secret Manager (see Step 3 in the section below).
5. From the **folder that contains the backend** (repo root with `Dockerfile`), run the `gcloud run deploy benchmarked-api ...` command.
6. Copy the Cloud Run URL and use it for the frontend (Vercel) and CORS.

---

## Prerequisites

- GitHub repo with code
- [Google AI Studio](https://aistudio.google.com/) – free Gemini API key
- [Supabase](https://supabase.com/) – free project (auth + DB)
- [Google Cloud](https://console.cloud.google.com/) – project with billing (free tier / $300 credit)
- [Vercel](https://vercel.com/) – free account

## 1. Supabase (Auth + rate limiting)

1. Create a project at [supabase.com](https://supabase.com).
2. **Authentication → Providers → Google**: Enable Google, create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials) (Web application, redirect URI `https://<project-ref>.supabase.co/auth/v1/callback`), paste Client ID and Secret.
3. **Authentication → URL Configuration** (required so production doesn’t redirect to localhost after Google Sign-In):
   - **Site URL**: your production URL, e.g. `https://benchmarked-ashen.vercel.app`
   - **Redirect URLs**: add `http://localhost:3000/**`, `http://localhost:3001/**`, `https://benchmarked-ashen.vercel.app/**`, and `https://*.vercel.app/**`
4. **SQL Editor**: Run the migration [supabase/migrations/001_user_usage.sql](supabase/migrations/001_user_usage.sql).
5. **Settings → API**: Note **Project URL**, **Publishable** key (client-safe; use as `SUPABASE_ANON_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`), **Secret** key (server-only; use as `SUPABASE_SERVICE_ROLE_KEY`), and **JWT Secret** (Settings → API → JWT Settings). Supabase may still show legacy labels “anon” and “service_role” for the same keys.

## 2. Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/) → Get API key → Create API key.
2. No credit card; free tier applies.

## 3. Backend – Google Cloud Run

**Important:** Use `gcloud run deploy` to **create** the service the first time. The command `gcloud run services update` only works **after** the service exists. If you see "Service [benchmarked-api] could not be found", run the **deploy** step below.

1. Create a GCP project and enable billing (free tier / $300 credit).
2. Set the region (so you can omit `--region` later):
   ```bash
   gcloud config set run/region us-central1
   ```
3. Enable APIs:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
   ```
4. Create secrets in Secret Manager **before** deploying (replace placeholders with your real values):
   ```bash
   echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   echo -n "https://YOUR_PROJECT_REF.supabase.co" | gcloud secrets create supabase-url --data-file=-
   echo -n "YOUR_SUPABASE_SECRET_KEY" | gcloud secrets create supabase-service-key --data-file=-
   echo -n "YOUR_SUPABASE_JWT_SECRET" | gcloud secrets create supabase-jwt-secret --data-file=-
   ```
   If a secret already exists, use `gcloud secrets versions add gemini-api-key --data-file=-` (and similar) to add a new version instead of `create`.
5. **Deploy** the service (this **creates** it; run from your project root where the Dockerfile lives):
   ```bash
   gcloud run deploy benchmarked-api \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "DEFAULT_AI_PROVIDER=gemini" \
     --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-key:latest,SUPABASE_JWT_SECRET=supabase-jwt-secret:latest" \
     --memory 512Mi --cpu 1 --timeout 300 --min-instances 0 --max-instances 3
   ```
   The first run builds the image and creates the service. Note the URL (e.g. `https://benchmarked-api-xxxxx-uc.a.run.app`).
6. **Later**, to change secrets or env vars on the **existing** service, use **update**:
   ```bash
   gcloud run services update benchmarked-api \
     --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,..."
   # or
   gcloud run services update benchmarked-api --set-env-vars "ALLOWED_ORIGINS=https://your-app.vercel.app"
   ```

## 4. Frontend – Vercel

1. Import the GitHub repo at [vercel.com](https://vercel.com); set **Root Directory** to `frontend`.
2. **Environment variables** (Production / Preview):
   - `NEXT_PUBLIC_API_BASE` = your Cloud Run URL (e.g. `https://benchmarked-api-xxxxx.run.app`)
   - `NEXT_PUBLIC_SUPABASE_URL` = Supabase Project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Supabase **Publishable** key (client-safe)
3. Deploy; Vercel will build and deploy on every push.

## 5. CORS

Add your Vercel URL to backend CORS. Either set env on Cloud Run:

```bash
gcloud run services update benchmarked-api --set-env-vars "ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app"
```

or in the Cloud Run console add `ALLOWED_ORIGINS` with your production and preview origins.

## 6. CI/CD (optional)

- **Vercel**: Auto-deploys frontend from GitHub; no extra config.
- **Cloud Run**: Use [.github/workflows/deploy-cloudrun.yml](.github/workflows/deploy-cloudrun.yml). Add secrets/variables:
  - **Secrets**: `GCP_SERVICE_ACCOUNT_KEY` = JSON key for a service account with Cloud Run Admin + Storage (for build).
  - **Variables**: `GCP_PROJECT_ID`, `GCP_REGION` (e.g. `us-central1`).

## 7. Scaling and limits

- **Per-user limit**: 2 comparisons per user per day (enforced in backend via Supabase `user_usage` table).
- **Gemini**: Free tier ~30–50 analyses/day; upgrade to paid in AI Studio for more (~$2–4/mo for 1K analyses).
- **Cloud Run**: Scales to zero; increase `--memory` or `--max-instances` if needed.
- **Supabase**: Free tier 50K MAU, 500MB DB; upgrade to Pro when needed.

## Cost summary

| Component   | Launch   | ~1K users      |
|------------|----------|----------------|
| Gemini     | $0       | $0–4/mo        |
| Supabase   | $0       | $0             |
| Cloud Run  | $0       | $0–10/mo       |
| Vercel     | $0       | $0             |
