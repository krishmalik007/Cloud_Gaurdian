# =============================================
# Cloud Guardian Backend - Multi-Stage Dockerfile
# =============================================

# ── Stage 1: Builder ──
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies for confluent-kafka (librdkafka)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ──
FROM python:3.12-slim

LABEL maintainer="Krish Malik"
LABEL description="Cloud Guardian - AI-Powered Multi-Cloud Threat Detection Backend"

WORKDIR /app

# Install runtime dependency for confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user for security
RUN groupadd -r cloudguardian && useradd -r -g cloudguardian cloudguardian
RUN chown -R cloudguardian:cloudguardian /app
USER cloudguardian

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
