# BenchMarked – Deployment Guide & Runbook

Purpose: End-to-end deployment instructions and operational troubleshooting reference.
Last Updated: 2026-03-28

---

## Prerequisites

- GitHub repo with code
- [Google AI Studio](https://aistudio.google.com/) – free Gemini API key
- [Supabase](https://supabase.com/) – free project (auth + DB)
- [Google Cloud](https://console.cloud.google.com/) – project with billing (free tier / $300 credit)
- [Vercel](https://vercel.com/) – free account

For local development see [SETUP_GUIDE.md](../SETUP_GUIDE.md) and [.env.example](../.env.example).

---

## 1. Supabase (Auth + Rate Limiting)

1. Create a project at [supabase.com](https://supabase.com).
2. **Authentication → Providers → Google**: Enable Google, create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials) (Web application, redirect URI `https://<project-ref>.supabase.co/auth/v1/callback`), paste Client ID and Secret.
3. **Authentication → URL Configuration**:
   - **Site URL**: your production URL, e.g. `https://benchmarked-ashen.vercel.app`
   - **Redirect URLs**: add `http://localhost:3000/**`, `http://localhost:3001/**`, `https://benchmarked-ashen.vercel.app/**`, and `https://*.vercel.app/**`
4. **SQL Editor**: Run the migration [supabase/migrations/001_user_usage.sql](../supabase/migrations/001_user_usage.sql).
5. **Settings → API**: Note **Project URL**, **Publishable** key (`SUPABASE_ANON_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`), and **Secret** key (`SUPABASE_SERVICE_ROLE_KEY`).
6. Backend JWT verification uses Supabase **JWKS** at `https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json` (asymmetric `ES256`/`RS256`), so no `SUPABASE_JWT_SECRET` is needed.

## 2. Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/) → Get API key → Create API key.
2. No credit card required; free tier applies.

## 3. Backend – Google Cloud Run

### Where to run `gcloud run deploy`

| Where you run the deploy command | Need to push & clone? |
|----------------------------------|------------------------|
| **Your laptop** (gcloud CLI)     | **No.** Run from your repo folder. |
| **Google Cloud Shell** (browser) | **Yes.** Push to GitHub, clone in Cloud Shell, deploy from clone. |

### Initial Setup

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

### Create Secrets (first time only)

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "https://YOUR_PROJECT_REF.supabase.co" | gcloud secrets create supabase-url --data-file=-
echo -n "YOUR_SUPABASE_SECRET_KEY" | gcloud secrets create supabase-service-key --data-file=-
```

To update an existing secret:

```bash
echo -n "NEW_VALUE" | gcloud secrets versions add gemini-api-key --data-file=-
```

### Deploy

Run from the project root (where `Dockerfile` lives):

```bash
gcloud run deploy benchmarked-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DEFAULT_AI_PROVIDER=gemini" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-key:latest" \
  --memory 512Mi --cpu 1 --timeout 300 --min-instances 0 --max-instances 3
```

Note the output URL (e.g. `https://benchmarked-api-xxxxx-uc.a.run.app`).

### Update Existing Service

```bash
gcloud run services update benchmarked-api \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,..."
# or
gcloud run services update benchmarked-api \
  --set-env-vars "ALLOWED_ORIGINS=https://your-app.vercel.app"
```

> `gcloud run services update` only works **after** the service exists. If you see "Service could not be found", use the full `deploy` command above.

## 4. Frontend – Vercel

1. Import the GitHub repo at [vercel.com](https://vercel.com); set **Root Directory** to `frontend`.
2. **Environment variables** (Production / Preview):
   - `NEXT_PUBLIC_API_BASE` = Cloud Run URL
   - `NEXT_PUBLIC_SUPABASE_URL` = Supabase Project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Supabase Publishable key
3. Deploy; Vercel auto-builds on push.

## 5. CORS

Add your Vercel URL to backend CORS:

```bash
gcloud run services update benchmarked-api \
  --update-env-vars ALLOWED_ORIGINS=https://benchmarked-ashen.vercel.app
```

## 6. CI/CD (Optional)

- **Vercel**: Auto-deploys frontend from GitHub; no extra config.
- **Cloud Run**: Workflow [.github/workflows/deploy-cloudrun.yml](../.github/workflows/deploy-cloudrun.yml) is **skipped by default**. To enable:
  1. Repo **Settings → Secrets → Actions**: add `GCP_SERVICE_ACCOUNT_KEY` (JSON key with Cloud Run Admin + Storage).
  2. Add variables `GCP_PROJECT_ID` and `GCP_REGION`.
  3. Add variable `CLOUD_RUN_DEPLOY` = `true`.

## 7. Scaling & Limits

- **Per-user limit**: 2 comparisons/user/day (enforced via Supabase `user_usage` table).
- **Gemini**: Free tier ~30–50 analyses/day; upgrade for more (~$2–4/mo for 1K analyses).
- **Cloud Run**: Scales to zero; increase `--memory` or `--max-instances` as needed.
- **Supabase**: Free tier 50K MAU, 500MB DB.

## Cost Summary

| Component  | Launch | ~1K users  |
|------------|--------|------------|
| Gemini     | $0     | $0–4/mo    |
| Supabase   | $0     | $0         |
| Cloud Run  | $0     | $0–10/mo   |
| Vercel     | $0     | $0         |

---

## Troubleshooting Runbook

### Post-Deploy Checklist

1. Update Cloud Run env vars (if changed).
2. Update secret bindings if Gemini or Supabase keys changed.
3. Clear browser cache, cookies, and local storage.
4. Log out & log in on the frontend to refresh JWT tokens.
5. Check frontend → backend requests:
   - `200 OK` → success
   - `401 Unauthorized` → invalid/expired token or signing key mismatch
   - CORS errors → check `ALLOWED_ORIGINS`

### View Logs

```bash
gcloud run logs read benchmarked-api --region us-central1 --limit 50
```

### JWT Notes

- Backend uses Supabase JWKS (`.well-known/jwks.json`) and accepts asymmetric JWTs only.
- Navigate to `Project Settings → API → JWT Settings` in Supabase to manage signing keys.
- Legacy HS256 key can stay revoked for this project.

### Common Issues

| Issue | Fix |
|-------|-----|
| `401 Unauthorized` | Sync signing keys/env vars; log out/in to refresh tokens |
| CORS errors | Verify `ALLOWED_ORIGINS` includes frontend URL |
| "Service could not be found" | Use `gcloud run deploy` (not `update`) for first deploy |
