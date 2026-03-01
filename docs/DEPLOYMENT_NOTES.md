# 🛠 benchmarked-api Deployment & Troubleshooting Notes

---

## ✅ Next Steps After Every Deploy

1. **Update Cloud Run environment variables** (if changed):

   ```bash
   gcloud run services update benchmarked-api --update-env-vars ALLOWED_ORIGINS=https://benchmarked-ashen.vercel.app
   ```

2. **Update Cloud Run secret bindings** if Gemini or Supabase service-role secret versions changed.

3. **Clear browser cache, cookies, and local storage.**
4. **Log out & log in on the frontend** to refresh JWT tokens.
5. **Check frontend → backend requests:**
   - `200 OK` → request succeeded
  - `401 Unauthorized` → invalid/expired token or signing key mismatch
   - CORS errors → check `ALLOWED_ORIGINS`
6. **View latest logs in Cloud Run:**

   ```bash
   gcloud run logs read benchmarked-api --region us-central1 --limit 50
   ```

## 1. Setup & Environment

### GCP Project & APIs

```bash
gcloud config set project benchmarked-488905
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

### Create Secrets in Secret Manager

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "https://YOUR_PROJECT_REF.supabase.co" | gcloud secrets create supabase-url --data-file=-
echo -n "YOUR_SUPABASE_SECRET_KEY" | gcloud secrets create supabase-service-key --data-file=-
```

### Add new secret versions when updating

```bash
echo -n "NEW_GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
echo -n "NEW_SUPABASE_SERVICE_ROLE_KEY" | gcloud secrets versions add supabase-service-key --data-file=-
```

## 2. Deploy Backend to Cloud Run

### Initial deploy

```bash
gcloud run deploy benchmarked-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DEFAULT_AI_PROVIDER=gemini" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-key:latest" \
  --memory 512Mi --cpu 1 --timeout 300 --min-instances 0 --max-instances 3
```

### Update environment variables (CORS)

```bash
gcloud run services update benchmarked-api --update-env-vars ALLOWED_ORIGINS=https://benchmarked-ashen.vercel.app
```

### JWT verification

Backend uses Supabase JWKS (`.well-known/jwks.json`) and accepts asymmetric JWTs (`ES256`/`RS256`) only.

## 3. Supabase JWT Secret / Signing Keys

- Navigate to `Project Settings → API → JWT Settings` in Supabase.
- Keep asymmetric JWT Signing Keys enabled (ECC/RSA).
- Legacy HS256 key can stay revoked for this project.

## 4. Frontend Setup & Deployment

- Deployed on Vercel from GitHub repo.
- Environment variables on Vercel:
  - `NEXT_PUBLIC_API_BASE` = Cloud Run URL (e.g., `https://benchmarked-api-xxxx.run.app`)
  - `NEXT_PUBLIC_SUPABASE_URL` = Supabase project URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Supabase publishable anon key

## 5. CORS Setup

Add Vercel frontend URL to Cloud Run backend:

```bash
gcloud run services update benchmarked-api --update-env-vars ALLOWED_ORIGINS=https://benchmarked-ashen.vercel.app
```

## 6. Troubleshooting & Testing

- Clear browser cache, cookies, and local storage before testing new deploys.
- Log out & log in to refresh JWT tokens.
- Check requests in Chrome DevTools → Network:
  - `200 OK` → request succeeded
  - `401 Unauthorized` → invalid/expired token or signing key mismatch
  - CORS errors → verify `ALLOWED_ORIGINS`
- View Cloud Run logs:

```bash
gcloud run logs read benchmarked-api --region us-central1 --limit 50
```

## 7. Key Commands Summary

```bash
# Set project & region
gcloud config set project benchmarked-488905
gcloud config set run/region us-central1

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# Create secrets
echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "https://your-project.supabase.co" | gcloud secrets create supabase-url --data-file=-
echo -n "your_supabase_service_role_key" | gcloud secrets create supabase-service-key --data-file=-

# Add new secret versions
echo -n "new_gemini_api_key" | gcloud secrets versions add gemini-api-key --data-file=-
echo -n "new_supabase_service_role_key" | gcloud secrets versions add supabase-service-key --data-file=-

# Deploy backend
gcloud run deploy benchmarked-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DEFAULT_AI_PROVIDER=gemini" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-key:latest" \
  --memory 512Mi --cpu 1 --timeout 300 --min-instances 0 --max-instances 3

# Update CORS
gcloud run services update benchmarked-api --update-env-vars ALLOWED_ORIGINS=https://benchmarked-ashen.vercel.app

# View logs
gcloud run logs read benchmarked-api --region us-central1 --limit 50
```

## 8. Future Session Context Note

**Context:**

- Project: `benchmarked-api` on Cloud Run (region `us-central1`).
- Backend validates JWT tokens from Supabase JWKS (asymmetric signing keys).
- Cloud Run env vars use Google Secret Manager (Gemini API key, Supabase URL, service role key).
- Frontend deployed on Vercel (`https://benchmarked-ashen.vercel.app`).
- Backend CORS includes frontend URL in `ALLOWED_ORIGINS`.
- Latest deploy revision: `benchmarked-api-00010-c5b`.
- Recent issues: `401 Unauthorized` and CORS errors resolved by syncing signing keys/env vars.