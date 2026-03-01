# OfferCompare Pro - Backend API (FastAPI)
# Platform-independent; use for local dev or production.

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run API on 8001; Cloud Run sets PORT at runtime
ENV PORT=8001
EXPOSE 8001
CMD ["sh", "-c", "exec python -m uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8001}"]
