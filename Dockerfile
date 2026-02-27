# OfferCompare Pro - Backend API (FastAPI)
# Platform-independent; use for local dev or production.

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run API on 8001 (match api_server.py)
ENV PORT=8001
EXPOSE 8001

CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8001"]
